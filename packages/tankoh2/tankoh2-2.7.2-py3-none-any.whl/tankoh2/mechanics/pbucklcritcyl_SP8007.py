import os
from copy import copy

import numpy as np
import pandas as pd
import patme
import yaml
from patme.service.stringutils import indent
from scipy.optimize import NonlinearConstraint, minimize

from tankoh2 import log, programDir
from tankoh2.masses.massestimation import getVesselMass
from tankoh2.mechanics.material import MaterialDefinition
from tankoh2.service.exception import Tankoh2Error

optLogger = log.debug  # whether optimization steps should be logged as debug or info
minRingPitch = 150
min_gap_between_rings = 20


def getRingParameterDict(paramKwArgs):
    ringKeys = [
        "ringCrossSectionType",
        "ringInertiaTransform",
        "ringInertiaTransformRatio",
        "ringHeight",
        "ringFootWidth",
        "ringWebHalfLayerThickness",
        "numberOfRings",
    ]
    # return ring_cross_section_type, inertia_transform, ringInertiaTransformRatio, ringHeight, ringFootWidth, ringWebHalfLayerThickness, nRings
    return {key: paramKwArgs[key] for key in ringKeys}


def checkStabilityMetal(
    burst_pressure,
    liner,
    minimal_cylinder_thickness,
    material,
    ringParameterDict,
    use_bk_hydrostatic,
    use_bk_safety_factor,
):
    """
    :param burst_pressure: burst pressure in bar
    :param liner: tankoh2 liner object
    :param minimal_cylinder_thickness: minimal thickness of cylinder from strength&fatigue calculation in mm
    :param material: material definition of type tankoh2.mechanics.material.MaterialDefinition
    :param ringParameterDict: dict with ring parameters:
        ["ringCrossSectionType","ringInertiaTransform","ringInertiaTransformRatio","ringHeight",
        "ringFootWidth","ringWebHalfLayerThickness","numberOfRings",]
    :param use_bk_hydrostatic: If true, in-plane axial load will be applied to the cylinder edges to represent
        the pressure applied to the domes
    :param use_bk_safety_factor: additional safety factor by 0.75, recommended in nasa SP8007.
        Can be omitted if a safety factor is already applied to burst_pressure
    :return:
    """
    results = stabilityOptMetal(
        liner,
        minimal_cylinder_thickness,
        material,
        ringParameterDict,
        burst_pressure,
        use_bk_hydrostatic,
        use_bk_safety_factor,
    )

    resultKeys = "wallThickness", "ringWebHalfLayerThickness", "numberOfRings", "metalMass"
    resultDict = {key: value for key, value in zip(resultKeys, results)}
    return resultDict


def stabilityOptMetal(
    liner,
    minimal_cylinder_thickness,
    material,
    ringParameterDict,
    burstPressure,
    hydrostatic_flag=False,
    safety_flag=False,
):
    ringKeys = [
        "ringCrossSectionType",
        "ringInertiaTransform",
        "ringInertiaTransformRatio",
        "ringHeight",
        "ringFootWidth",
        "ringWebHalfLayerThickness",
        "numberOfRings",
    ]
    (
        ring_cross_section_type,
        inertia_transform,
        ringInertiaTransformRatio,
        ringHeight,
        ringFootWidth,
        ringWebHalfLayerThickness,
        numberOfRings,
    ) = [ringParameterDict[key] for key in ringKeys]

    # opt values: cylinder thickness, ring web half thickness, number of rings
    x0 = [minimal_cylinder_thickness, minimal_cylinder_thickness, 5]

    # bounds
    min_rings, max_rings = calculate_minimum_nrings(liner.lcyl, ringFootWidth)
    bounds = np.array(
        [
            (minimal_cylinder_thickness, minimal_cylinder_thickness * 5),
            (
                np.min([1, minimal_cylinder_thickness]),
                np.max([minimal_cylinder_thickness * 5, 4]),
            ),  # web half thickness
            (min_rings, max_rings),
        ]
    )
    optLogger("X0 and bounds:\n" + indent([["skinThk", "halfWebThk", "nRings"]] + [x0] + list(np.array(bounds).T)))

    # constraints
    localBuckConstriantFunction = BucklingConstraintFunction(liner, material, hydrostatic_flag, safety_flag)
    localBuckConstriantFunction.usedConstraintFunction = localBuckConstriantFunction.getCritPressureMetalLocalBuck
    localBuckConstriant = NonlinearConstraint(localBuckConstriantFunction, burstPressure, np.inf)
    globalBuckConstriantFunction = BucklingConstraintFunction(
        liner, material, ringParameterDict, hydrostatic_flag, safety_flag
    )
    globalBuckConstriantFunction.usedConstraintFunction = globalBuckConstriantFunction.getCritPressureMetalGlobalBuck
    globalBuckConstraint = NonlinearConstraint(globalBuckConstriantFunction, burstPressure, np.inf)
    constraints = [localBuckConstriant, globalBuckConstraint]

    # arguments to opt function
    args = [liner, material, ring_cross_section_type, [0], ringHeight, ringFootWidth]

    res = minimize(
        optTargetFunctionMetal,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        args=args,
        options={"ftol": 1e-2},
    )
    if not res.success:
        log.error(f"Optimization did not terminated successully: {res.message}")
    optLogger(f"x, fun, comment: {res.x, res.fun, res.message}")
    x = copy(res.x)
    x[2] = int(np.ceil(x[2]))
    resMass = optTargetFunctionMetal(x, args)

    return *x, resMass


def optTargetFunctionMetal(x, args):
    cylinder_thickness, webHalfThickness, nRings = x
    liner, material, ring_cross_section_type, ring_stacking, ringHeight, ringFootWidth = args
    pitch = getPitch(liner.lcyl, nRings)

    cross_section = getCrossSection(ring_cross_section_type, webHalfThickness, ring_stacking, ringHeight, ringFootWidth)
    ringMassPerArea = cross_section.getAreaMass(material, pitch)
    mass = getVesselMass(liner, cylinder_thickness, material.rho, ringMassPerArea)

    optLogger(f"Mass x: {x} mass: {mass}")
    return mass


def getCritPressureMetalLocalBuck(
    radius, axial_length, cylinder_thickness, material_cylinder, hydrostatic_flag=False, safety_flag=False
):
    """Calculates the critical pressure for all half waves"""
    layup = [0]
    _, cylinderAbdMatrix, _ = calculate_SP8007_stiffness(layup, cylinder_thickness, material_cylinder)

    n_range = range(2, 201)  # circumferential half waves
    m_range = range(1, 21) if hydrostatic_flag else range(1, 2)  # axial half waves
    m_cr = min(m_range)
    n_cr = min(n_range)
    lowestCriticalPressure = float("inf")
    for m in m_range:
        for n in n_range:
            pressure = getCritPressureFixedHalfWaves(
                radius, axial_length, m, n, None, None, hydrostatic_flag, True, safety_flag, cylinderAbdMatrix
            )
            if pressure < lowestCriticalPressure:
                lowestCriticalPressure = pressure
                m_cr = m
                n_cr = n
    optLogger(f"Local Buckling m,n: {m_cr, n_cr}")
    return lowestCriticalPressure


def getCritPressureMetalGlobalBuck(
    radius,
    axial_length,
    cylinder_thickness,
    material_cylinder,
    ringParameterDict,
    hydrostatic_flag=False,
    safety_flag=False,
):
    """Calculates the critical pressure for all half waves"""
    layup = [0]
    _, cylinderAbdMatrix, _ = calculate_SP8007_stiffness(layup, cylinder_thickness, material_cylinder)

    n_range = range(2, 51)  # circumferential half waves
    m_range = range(1, 21) if hydrostatic_flag else range(1, 2)  # axial half waves
    ringKeys = [
        "ringCrossSectionType",
        "ringInertiaTransform",
        "ringInertiaTransformRatio",
        "ringHeight",
        "ringFootWidth",
        "ringWebHalfLayerThickness",
        "numberOfRings",
    ]
    (
        ring_cross_section_type,
        inertia_transform,
        ringInertiaTransformRatio,
        ringHeight,
        ringFootWidth,
        ringWebHalfLayerThickness,
        numberOfRings,
    ) = [ringParameterDict[key] for key in ringKeys]
    pitch = getPitch(axial_length, numberOfRings)
    (
        extensional_stiffness,
        bending_stiffness,
        twisting_stiffness,
        coupling_stiffness,
        ring_weight_per_meter,
        ring_stacking,
        n_basic_laminate,
    ) = calculateCrossSectionConstant(
        ring_cross_section_type,
        pitch,
        layup,
        None,
        ringWebHalfLayerThickness,
        material_cylinder,
        material_cylinder.rho,
        inertia_transform,
        ringInertiaTransformRatio,
        cylinder_thickness,
        ringHeight,
        ringFootWidth,
    )

    check_ring, constraint = check_ring_stiffness(
        cylinderAbdMatrix, extensional_stiffness, bending_stiffness, twisting_stiffness
    )
    if not check_ring:
        log.info(
            "The rings provide an additional stiffness that likely will be associate with non-conservative "
            f"results with following constraints: {constraint}"
        )

    lowestCriticalPressure = float("inf")
    m_global = min(m_range)
    n_global = min(n_range)
    ring_stiffness = [extensional_stiffness, bending_stiffness, twisting_stiffness, coupling_stiffness]
    for m in m_range:
        for n in n_range:
            pressure_global = getCritPressureFixedHalfWaves(
                radius,
                axial_length,
                m,
                n,
                ring_stiffness,
                None,
                hydrostatic_flag,
                False,
                safety_flag,
                cylinderAbdMatrix,
            )
            log.debug(f"{pressure_global, m,n}")
            if pressure_global < lowestCriticalPressure:
                lowestCriticalPressure = pressure_global
                m_global = m
                n_global = n

    optLogger(f"global buckling m, n: {m_global, n_global}")
    return lowestCriticalPressure


def checkStabilityCFRP(
    burst_pressure,
    liner,
    cylinder_layup,
    ply_thickness,
    materialCylinder,
    ringDefinitionFile,
    use_bk_hydrostatic,
    use_bk_safety_factor,
    return_all=False,
):
    """

    :param burst_pressure: burst pressure in bar
    :param liner: tankoh2 liner object
    :param cylinder_layup: as list of angles in °
    :param ply_thickness: thickness of one ply in mm
    :param materialCylinder: material definition of type tankoh2.mechanics.material.MaterialDefinition
    :param ringDefinitionFile: yaml file with ring definition data. An example can be found in /data/default_ring.yaml
    :param use_bk_hydrostatic: If true, in-plane axial load will be applied to the cylinder edges to represent
        the pressure applied to the domes
    :param use_bk_safety_factor: additional safety factor by 0.75, recommended in nasa SP8007.
        Can be omitted if a safety factor is already applied to burst_pressure
    :param return_all:
    :return:
    """

    cylinder_layup = balanced_symmetric(cylinder_layup)
    results = calculate_designs_for_layups_and_pitches(
        liner.rCyl,
        liner.lcyl,
        cylinder_layup,
        ply_thickness,
        materialCylinder,
        ringDefinitionFile,
        None,
        use_bk_hydrostatic,
        use_bk_safety_factor,
    )

    if return_all:
        return results
    else:
        results = results.sort_values(by="ring_weight")
        if np.any(results["p_cr"] >= burst_pressure):
            results = results[results["p_cr"] >= burst_pressure]
            best_design = results.loc[results["ring_weight"].idxmin()]
        else:
            # best_design = results.loc[results["p_cr"].idxmax()]
            raise Tankoh2Error(
                f"Could not find a buckling solution that suffices the given burst pressure. Parameters: {burst_pressure, liner, cylinder_layup, ply_thickness, materialCylinder, ringDefinitionFile, use_bk_hydrostatic, use_bk_safety_factor}"
            )

        return (
            best_design["p_cr"],
            best_design["ring_weight"],
            best_design["n_rings"],
            best_design["global_or_local_buckling"],
            best_design["ring_laminate"],
            best_design["n_basic_ring_laminate"],
        )


def get_lamina_stiffness_matrix(material):
    e1, e2, nu12, g12, g13, g23 = (
        material.moduli["e11"],
        material.moduli["e22"],
        material.moduli["nu12"],
        material.moduli["g12"],
        material.moduli["g13"],
        material.moduli["g23"],
    )

    if e2 in (None, 0, 0.0):
        e2 = e1
        g12 = e1 / (2.0 * (1.0 + nu12))

    nu21 = nu12 * e2 / e1
    aux_var = 1.0 - nu12 * nu21

    return np.array(
        [[e1 / aux_var, nu12 * e2 / aux_var, 0.0], [nu12 * e2 / aux_var, e2 / aux_var, 0.0], [0.0, 0.0, g12]]
    )


def calculate_transform_matrix(angle):

    m = np.cos(np.deg2rad(angle))
    n = np.sin(np.deg2rad(angle))

    t_inv_t = np.array(
        [[m**2.0, n**2.0, m * n], [n**2.0, m**2.0, -m * n], [-2.0 * m * n, 2.0 * m * n, m**2.0 - n**2.0]]
    )
    t_inv = np.array([[m**2.0, n**2.0, -2.0 * m * n], [n**2.0, m**2.0, 2.0 * m * n], [m * n, -m * n, m**2.0 - n**2.0]])

    return t_inv_t, t_inv


def calculate_SP8007_stiffness(layup, ply_thickness, materialCylinder):

    n_plies = len(layup)
    laminate_thickness = ply_thickness * n_plies

    a_matrix, b_matrix, d_matrix = np.zeros((3, 3)), np.zeros((3, 3)), np.zeros((3, 3))
    for count, angle in enumerate(layup):
        q_matrix = get_lamina_stiffness_matrix(materialCylinder)
        t_inv_t, t_inv = calculate_transform_matrix(angle)
        q_bar = np.dot(np.dot(t_inv, q_matrix), t_inv_t)

        zbar = -(laminate_thickness + ply_thickness) / 2 + (count + 1) * ply_thickness
        a_matrix += q_bar * ply_thickness
        b_matrix += q_bar * ply_thickness * zbar
        d_matrix += q_bar * ply_thickness * (zbar**2 + ply_thickness**2 / 12)

    abd_matrix = np.block([[a_matrix, b_matrix], [b_matrix, d_matrix]])
    abd_matrix[np.abs(abd_matrix) < patme.epsilon] = 0

    abd_inv = np.linalg.inv(abd_matrix)

    axx, ayy, ass = abd_inv[0, 0], abd_inv[1, 1], abd_inv[2, 2]
    ayx, axy, axs, asx, asy, ays = (
        abd_inv[1, 0],
        abd_inv[0, 1],
        abd_inv[0, 2],
        abd_inv[2, 0],
        abd_inv[2, 1],
        abd_inv[1, 2],
    )

    laminate_properties = dict(
        Exbar=1 / (laminate_thickness * axx),
        Eybar=1 / (laminate_thickness * ayy),
        Gxybar=1 / (laminate_thickness * ass),
        nuxybar=-ayx / axx,
        nuyxbar=-axy / ayy,
        etasxbar=axs / ass,
        etaxsbar=asx / axx,
        etaysbar=asy / ayy,
        etasybar=ays / ass,
    )

    return laminate_properties, abd_matrix, laminate_thickness


def retrieve_abd_matrix(param_dict, material_dict, lam_thickness):

    q_matrix = get_lamina_stiffness_matrix(material_dict)

    ue = (3.0 * q_matrix[0, 0] + 3.0 * q_matrix[1, 1] + 2.0 * q_matrix[0, 1] + 4.0 * q_matrix[2, 2]) / 8.0
    ug = (q_matrix[0, 0] + q_matrix[1, 1] - 2.0 * q_matrix[0, 1] + 4.0 * q_matrix[2, 2]) / 8.0
    udc = (q_matrix[0, 0] - q_matrix[1, 1]) / 2.0
    unuc = (q_matrix[0, 0] + q_matrix[1, 1] - 2.0 * q_matrix[0, 1] - 4.0 * q_matrix[2, 2]) / 8.0

    ie = np.array([[1, 1, 0], [1, 1, 0], [0, 0, 0]])
    ig = np.array([[0, -2, 0], [-2, 0, 0], [0, 0, 1]])
    i1 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]])
    i2 = np.array([[0, 0, 0.5], [0, 0, 0.5], [0.5, 0.5, 0]])
    i3 = np.array([[1, -1, 0], [-1, 1, 0], [0, 0, -1]])
    i4 = np.array([[0, 0, 1], [0, 0, -1], [1, -1, 0]])

    xsi_a_vec, xsi_b_vec, xsi_d_vec = param_dict.values()

    a_matrix = (
        ue * ie
        + ug * ig
        + xsi_a_vec[0] * udc * i1
        + xsi_a_vec[1] * udc * i2
        + xsi_a_vec[2] * unuc * i3
        + xsi_a_vec[3] * unuc * i4
    ) * lam_thickness
    b_matrix = (
        (
            ue * ie
            + ug * ig
            + xsi_b_vec[0] * udc * i1
            + xsi_b_vec[1] * udc * i2
            + xsi_b_vec[2] * unuc * i3
            + xsi_b_vec[3] * unuc * i4
        )
        * lam_thickness**2
        / 4
    )
    d_matrix = (
        (
            ue * ie
            + ug * ig
            + xsi_d_vec[0] * udc * i1
            + xsi_d_vec[1] * udc * i2
            + xsi_d_vec[2] * unuc * i3
            + xsi_d_vec[3] * unuc * i4
        )
        * lam_thickness**3
        / 12
    )

    abd_matrix = np.block([[a_matrix, b_matrix], [b_matrix, d_matrix]])
    abd_inv = np.linalg.inv(abd_matrix)

    axx, ayy, ass = abd_inv[0, 0], abd_inv[1, 1], abd_inv[2, 2]
    ayx, axy, axs, asx, asy, ays = (
        abd_inv[1, 0],
        abd_inv[0, 1],
        abd_inv[0, 2],
        abd_inv[2, 0],
        abd_inv[2, 1],
        abd_inv[1, 2],
    )

    laminate_properties = dict(
        Exbar=1 / (lam_thickness * axx),
        Eybar=1 / (lam_thickness * ayy),
        Gxybar=1 / (lam_thickness * ass),
        nuxybar=-ayx / axx,
        nuyxbar=-axy / ayy,
        etasxbar=axs / ass,
        etaxsbar=asx / axx,
        etaysbar=asy / ayy,
        etasybar=ays / ass,
    )

    return laminate_properties, abd_matrix


def calculate_lamination_parameters(lamination_angles, ply_thickness, material_dict, abd_flag):

    n_plies = len(lamination_angles)
    lam_thickness = ply_thickness * n_plies

    xsi_a_vec, xsi_b_vec, xsi_d_vec = np.zeros((4, 1)), np.zeros((4, 1)), np.zeros((4, 1))

    for count, angle in enumerate(lamination_angles):
        theta = np.deg2rad(angle)

        aux_vec = np.array([[np.cos(2 * theta)], [np.sin(2 * theta)], [np.cos(4 * theta)], [np.sin(4 * theta)]])
        zbar = -(lam_thickness + ply_thickness) / 2 + (count + 1) * ply_thickness
        xsi_a_vec += aux_vec
        xsi_b_vec += aux_vec * zbar
        xsi_d_vec += aux_vec * ply_thickness * (12 * zbar**2 + ply_thickness**2)

    xsi_a_vec = xsi_a_vec / n_plies
    xsi_b_vec = 4 * xsi_b_vec / (n_plies * lam_thickness)
    xsi_d_vec = xsi_d_vec / lam_thickness**3

    lamination_parameters = dict(xsi_a_vec=xsi_a_vec, xsi_b_vec=xsi_b_vec, xsi_d_vec=xsi_d_vec)

    if abd_flag:
        laminate_properties, abd_matrix = retrieve_abd_matrix(lamination_parameters, material_dict, lam_thickness)
        return laminate_properties, abd_matrix, lamination_parameters, lam_thickness

    else:
        return lamination_parameters, lam_thickness


def check_lamination_parameters(lamination_parameters):

    # TODO: In case of an optimization strategy based on lamination parameters, this function must be defined for
    #  checking the design space

    xsi_a_vec, xsi_b_vec, xsi_d_vec = lamination_parameters.values()
    xsi_vec = xsi_a_vec + xsi_d_vec
    constraint = [
        2 * xsi_vec[0] ** 2 * (1 - xsi_vec[2])
        + 2 * xsi_vec[1] ** 2 * (1 + xsi_vec[2])
        + xsi_vec[2] ** 2
        + xsi_vec[3] ** 2
        - 4 * xsi_vec[0] * xsi_vec[1] * xsi_vec[3]
        <= 1,
        xsi_vec[0] ** 2 + xsi_vec[1] ** 2 <= 1,
        2 * xsi_vec[4] ** 2 * (1 - xsi_vec[6])
        + 2 * xsi_vec[5] ** 2 * (1 + xsi_vec[6])
        + xsi_vec[6] ** 2
        + xsi_vec[7] ** 2
        - 4 * xsi_vec[4] * xsi_vec[5] * xsi_vec[7]
        <= 1,
        xsi_vec[4] ** 2 + xsi_vec[5] ** 2 <= 1,
        0.25 * xsi_vec[0] ** 3 + 0.75 * xsi_vec[0] ** 2 + 0.75 * xsi_vec[0] - xsi_vec[4] <= 0.75,
        -0.25 * xsi_vec[0] ** 3 + 0.75 * xsi_vec[0] ** 2 - 0.75 * xsi_vec[0] + xsi_vec[4] <= 0.75,
        0.25 * xsi_vec[2] ** 3 + 0.75 * xsi_vec[2] ** 2 + 0.75 * xsi_vec[2] - xsi_vec[6] <= 0.75,
        -0.25 * xsi_vec[2] ** 3 + 0.75 * xsi_vec[2] ** 2 - 0.75 * xsi_vec[2] + xsi_vec[6] <= 0.75,
        1.75 * xsi_vec[0] ** 4 + 0.19 * xsi_vec[0] ** 2 - xsi_vec[6] <= 1,
        1.31 * xsi_vec[4] ** 6 - 1.2 * xsi_vec[4] ** 4 + 1.38 * xsi_vec[4] ** 2 - xsi_vec[2] <= 1,
    ]

    if not all(constraint):
        return False

    if not all(-1 <= x <= 1 for x in xsi_vec):
        return False

    return True


def calculate_buckling_determinant(
    stiffness_matrix,
    radius,
    axial_length,
    axial_halfwaves,
    circumferential_waves,
    ring_stiffness=None,
    stringer_stiffness=None,
):

    mm = axial_halfwaves * np.pi / axial_length
    mm2 = mm * mm
    nn = circumferential_waves / radius
    nn2 = nn * nn

    _ex_bar, _ey_bar, _exy_bar, _gxy_bar = [
        stiffness_matrix[0, 0],
        stiffness_matrix[1, 1],
        stiffness_matrix[0, 1],
        stiffness_matrix[2, 2],
    ]
    _dx_bar, _dy_bar, _dxy_bar = [stiffness_matrix[3, 3], stiffness_matrix[4, 4], stiffness_matrix[3, 4]]
    _cx_bar, _cy_bar, _cxy_bar, _kxy_bar = [
        stiffness_matrix[0, 3],
        stiffness_matrix[1, 4],
        stiffness_matrix[0, 4],
        stiffness_matrix[2, 5],
    ]

    if ring_stiffness is not None:
        _ey_bar += ring_stiffness[0]
        _dy_bar += ring_stiffness[1]
        _dxy_bar += ring_stiffness[2]
        _cy_bar += ring_stiffness[3]

    if stringer_stiffness is not None:
        _ex_bar += stringer_stiffness[0]
        _dx_bar += stringer_stiffness[1]
        _dxy_bar += stringer_stiffness[2]
        _cx_bar += stringer_stiffness[3]

    a11 = _ex_bar * mm2 + _gxy_bar * nn2
    a12 = (_exy_bar + _gxy_bar) * mm * nn
    a13 = (_exy_bar / radius) * mm + _cx_bar * mm**3 + (_cxy_bar + 2 * _kxy_bar) * mm * nn2
    a22 = _gxy_bar * mm2 + _ey_bar * nn2
    a23 = (_cxy_bar + 2 * _kxy_bar) * mm2 * nn + (_ey_bar / radius) * nn + _cy_bar * nn**3
    a33 = (
        _dx_bar * mm2**2
        + _dxy_bar * mm2 * nn2
        + _dy_bar * nn2**2
        + _ey_bar / (radius**2)
        + (2 * _cy_bar / radius) * nn2
        + (2 * _cxy_bar / radius) * mm2
    )

    det3_over_det2 = a33 + (a23 * (a13 * a12 - a11 * a23) + a13 * (a12 * a23 - a13 * a22)) / (a11 * a22 - a12**2)

    return det3_over_det2


def check_ring_stiffness(stiffness_matrix, extensional_stiffness, bending_stiffness, twisting_stiffness, tol=5000):

    ey_bar = stiffness_matrix[1, 1]
    dy_bar, dxy_bar = stiffness_matrix[4, 4], stiffness_matrix[3, 4]

    ey_bar_ring = extensional_stiffness
    dy_bar_ring = bending_stiffness
    dxy_bar_ring = twisting_stiffness

    constraint = [
        ey_bar_ring / ey_bar < tol,
        dy_bar_ring / dy_bar < tol * 100,
        dxy_bar_ring / dxy_bar < tol,
    ]

    if not all(constraint):
        log.info("At least one of the stiffness components of the rings is out of the boundaries.")
        return False, [ey_bar_ring / ey_bar, dy_bar_ring / dy_bar, dxy_bar_ring / dxy_bar]

    return True, None


def balanced_symmetric(layup_sequence):

    layup_complete = []
    for item in layup_sequence:
        layup_complete.extend([item, -item])
    layup_complete = [abs(item) if item in (-0, -90) else item for item in layup_complete]
    layup_complete = layup_complete + layup_complete[::-1]

    return layup_complete


def calculate_minimum_nrings(axial_length, ringFootWidth, max_pitch_factor=5):
    """
    Suggests a maximum distance between rings, so the ring stiffnesses can be properly smeared in the cylinder
    thickness.
    """

    # TODO: Maybe include here a rule that depends on the smeared stiffness, not on the geometry. This "If L/R is
    #  equal or smaller than 2, the maximum distance is a fraction of the radius, otherwise the axial length is used
    #  as a reference." was tested and it does not solve for small tanks.
    #  TODO: Once it is finished, remove the radius as input.

    min_pitch = np.max([ringFootWidth + min_gap_between_rings, minRingPitch])

    max_pitch = axial_length / max_pitch_factor
    num_rings = axial_length / max_pitch
    min_rings = int(num_rings) if num_rings.is_integer() else int(num_rings) + 1
    num_rings = axial_length / min_pitch
    max_rings = int(num_rings)

    if min_rings > max_rings:
        min_rings = max_rings

    return min_rings, max_rings


def getCritPressureFixedHalfWaves(
    radius,
    axial_length,
    m,
    n,
    ring_stiffness,
    stringer_stiffness,
    hydrostatic_flag,
    local_flag,
    safety_flag,
    cylinderAbdMatrix,
):
    """
    It is common for metallic tanks sized by ASME code 2 part section 3 to consider 30% of the dome height as part
    of the cylindrical length. Here it is assumed that the dome is torispherical and follows r1ToD0=0.8 and
    r2ToD0=0.154, resulting in h_dome = 0.66 * radius
    """
    h_dome = 0.66 * radius  # Calculated based on torispherical geometry
    length_factor = 0.3
    sf_factor = 0.75

    axial_length = axial_length if local_flag else axial_length + (2 * length_factor * h_dome)
    det3_over_det2 = calculate_buckling_determinant(
        cylinderAbdMatrix, radius, axial_length, m, n, ring_stiffness, stringer_stiffness
    )
    aux_var = n**2.0 + 0.5 * (m * np.pi * radius / axial_length) ** 2.0 if hydrostatic_flag else n**2.0
    p_cr = (radius / aux_var) * det3_over_det2
    if safety_flag:
        p_cr *= sf_factor
    return p_cr


def calculate_designs_for_layups_and_pitches(
    radius,
    axial_length,
    cylinderLayup,
    ply_thickness,
    materialCylinder,
    ring_yaml=None,
    stringer_yaml=None,
    hydrostatic_flag=False,
    safety_flag=False,
):
    # TODO: the local buckling criterion must be revised for short cylinders, as it may produce too conservative results
    #  for short cylinders.
    ringFootWidth = 50
    _, cylinderAbdMatrix, _laminate_thickness = calculate_SP8007_stiffness(
        cylinderLayup, ply_thickness, materialCylinder
    )
    n_range = range(2, 201)  # circumferential half waves
    m_range = range(1, 21) if hydrostatic_flag else range(1, 2)  # axial half waves

    if ring_yaml is None and stringer_yaml is None:
        results = [["p_cr", "m", "n"]]
        opt_p_cr = float("inf")
        m_cr = min(m_range)
        n_cr = min(n_range)
        for m in m_range:
            for n in n_range:
                pressure = getCritPressureFixedHalfWaves(
                    radius, axial_length, m, n, None, None, hydrostatic_flag, True, safety_flag, cylinderAbdMatrix
                )
                if pressure < opt_p_cr:
                    opt_p_cr = pressure
                    m_cr = m
                    n_cr = n
        results.append([opt_p_cr, m_cr, n_cr])

    elif ring_yaml is not None and stringer_yaml is None:
        results = [
            [
                "n_rings",
                "ring_laminate",
                "n_basic_ring_laminate",
                "global_or_local_buckling",
                "p_cr",
                "ring_weight",
                "p_cr_local",
                "m_local",
                "n_local",
                "p_cr_global",
                "m_global",
                "n_global",
            ]
        ]
        min_rings, max_rings = calculate_minimum_nrings(axial_length, ringFootWidth)

        for n_rings_ite in range(min_rings, max_rings + 1):
            log.debug("n_rings: ", n_rings_ite)
            pitch = getPitch(axial_length, n_rings_ite)
            rings_stiffnesses = calculateCrossSectionConstantsByStackingMultiplyer(
                ring_yaml, pitch, _laminate_thickness, ringFootWidth
            )

            for ring_parameters in rings_stiffnesses:

                (
                    extensional_stiffness,
                    bending_stiffness,
                    twisting_stiffness,
                    coupling_stiffness,
                    ring_weight_per_meter,
                    ring_stacking,
                    n_basic_laminate,
                ) = ring_parameters
                log.debug("n_basic_laminate: ", n_basic_laminate)

                check_ring, constraint = check_ring_stiffness(
                    cylinderAbdMatrix, extensional_stiffness, bending_stiffness, twisting_stiffness
                )
                if not check_ring:
                    log.info(
                        "The rings provide an additional stiffness that likely will be associate with non-conservative "
                        "results with following constraints: {1}".format(n_rings_ite, constraint)
                    )

                opt_p_cr_global = float("inf")
                m_global = min(m_range)
                n_global = min(n_range)

                opt_p_cr_local = float("inf")
                m_local = min(m_range)
                n_local = min(n_range)

                for m in m_range:
                    for n in n_range:
                        pressure_global = getCritPressureFixedHalfWaves(
                            radius,
                            axial_length,
                            m,
                            n,
                            [extensional_stiffness, bending_stiffness, twisting_stiffness, coupling_stiffness],
                            None,
                            hydrostatic_flag,
                            False,
                            safety_flag,
                            cylinderAbdMatrix,
                        )
                        if pressure_global < opt_p_cr_global:
                            opt_p_cr_global = pressure_global
                            m_global = m
                            n_global = n

                        pressure_local = getCritPressureFixedHalfWaves(
                            radius, pitch, m, n, None, None, hydrostatic_flag, True, safety_flag, cylinderAbdMatrix
                        )
                        if pressure_local < opt_p_cr_local:
                            opt_p_cr_local = pressure_local
                            m_local = m
                            n_local = n

                results.append(
                    [
                        n_rings_ite,
                        ring_stacking,
                        n_basic_laminate,
                        "local" if opt_p_cr_global > opt_p_cr_local else "global",
                        opt_p_cr_local if opt_p_cr_global > opt_p_cr_local else opt_p_cr_global,
                        ring_weight_per_meter * n_rings_ite * 2 * np.pi * radius,
                        opt_p_cr_local,
                        m_local,
                        n_local,
                        opt_p_cr_global,
                        m_global,
                        n_global,
                    ]
                )

    elif ring_yaml is None and stringer_yaml is not None:
        results = [" ", " "]
        raise NotImplementedError("")

    else:  # case of stringers and rings
        results = [" ", " "]
        raise NotImplementedError("")

    df = pd.DataFrame(results[1:], columns=results[0])

    return df


def optimize_critical_pressure(
    target_pressure, radius, axial_length, initial_angle, h_ply, material, hydrostatic_flag=True, ratio_rings=0.5
):
    """Performs the optimization layer by layer; not good results

    # opt_pr, layup = optimize_critical_pressure(0.2, 2500, 2486.35, 5.89, h_ply, material)

    """

    angles_step_1 = np.linspace(0, 90, 1001)

    i_layup = [initial_angle, 0]
    count = 1
    opt_p = 0.0

    while opt_p < target_pressure * ratio_rings:
        for i_angle in angles_step_1:
            i_layup[count] = i_angle
            _complete_layup = balanced_symmetric(i_layup)
            _, pressure = calculate_designs_for_layups_and_pitches(
                radius, axial_length, _complete_layup, h_ply, material, None, None, hydrostatic_flag
            )
            if pressure > opt_p:
                opt_p = pressure
                best_angle = i_angle
        i_layup[count] = best_angle
        log.info("_layup: ", i_layup)
        i_layup.append(0)
        count += 1

    return opt_p, i_layup[:-1]


def read_ring_yaml(yaml_file):

    with open(os.path.join(programDir, "data", yaml_file + ".yaml"), "r") as yaml_file:
        data = yaml.safe_load(yaml_file)

    (
        ring_cross_section_type,
        ring_lamination_angles,
        ring_ply_thickness,
        ringMaterialName,
        ring_rho,
        ring_inertia_transform,
        ringInertiaTransformRatio,
    ) = data.values()

    ringMaterialName = ringMaterialName if ringMaterialName.endswith(".json") else ringMaterialName + ".json"
    ringMaterialFileName = ringMaterialName
    if not os.path.exists(ringMaterialName):
        ringMaterialFileName = os.path.join(programDir, "data", ringMaterialName)
    ringMaterial = MaterialDefinition().getMaterialFromMuWindJsonFile(ringMaterialFileName)

    return (
        ring_cross_section_type,
        ring_lamination_angles,
        ring_ply_thickness,
        ringMaterial,
        ring_rho,
        ring_inertia_transform,
        ringInertiaTransformRatio,
    )


def n_ring_stacking_sequence(basic_laminate_thickness, cylinder_thickness):

    # todo: Verify if this criterion could be improved

    max_symmetry = int((cylinder_thickness / 2) // basic_laminate_thickness)

    if max_symmetry == 0:
        return [1, 2]

    elif max_symmetry == 1:
        return [1, 2, 3]

    else:
        return list(range(max_symmetry, max_symmetry + 3))


def getPitch(axial_length, numberOfRings):
    return axial_length / (numberOfRings + 1)


def calculateCrossSectionConstantsByStackingMultiplyer(yaml_file, pitch, cylinder_thickness, footWidth):
    """"""
    (
        ring_cross_section_type,
        lamination_angles,
        ply_thickness,
        material,
        rho,
        inertia_transform,
        ringInertiaTransformRatio,
    ) = read_ring_yaml(yaml_file)

    n_plies = len(lamination_angles)
    basic_laminate_thickness = ply_thickness * n_plies
    number_of_different_rings = n_ring_stacking_sequence(basic_laminate_thickness, cylinder_thickness)

    rings_stiffnesses = []

    for n_basic_stacking_ring in number_of_different_rings:
        ring_stacking = lamination_angles * n_basic_stacking_ring
        rings_stiffnesses.append(
            calculateCrossSectionConstant(
                ring_cross_section_type,
                pitch,
                ring_stacking,
                n_basic_stacking_ring,
                ply_thickness,
                material,
                rho,
                inertia_transform,
                ringInertiaTransformRatio,
                cylinder_thickness,
                footWidth=footWidth,
            )
        )
    return rings_stiffnesses


def calculateCrossSectionConstant(
    ring_cross_section_type,
    pitch,
    ring_stacking,
    n_basic_stacking_ring,
    ply_thickness,
    material,
    rho,
    inertia_transform,
    ringInertiaTransformRatio,
    cylinder_thickness,
    ringHeight=None,
    footWidth=None,
):

    laminate_properties_web, _, _ = calculate_SP8007_stiffness(
        ring_stacking + ring_stacking[::-1], ply_thickness, material
    )
    laminate_properties_base, _, _ = calculate_SP8007_stiffness(ring_stacking, ply_thickness, material)
    e_bar_web, g_bar_web = laminate_properties_web["Exbar"], laminate_properties_web["Gxybar"]
    e_bar_base, g_bar_base = laminate_properties_base["Exbar"], laminate_properties_base["Gxybar"]

    cross_section = getCrossSection(ring_cross_section_type, ply_thickness, ring_stacking, ringHeight, footWidth)

    area_web = cross_section.area_web
    area_base = cross_section.area_base
    centroid_y_web = cross_section.centroid_y_web
    centroid_y_base = cross_section.centroid_y_base

    zy_web, zy_base = 0.0, 0.0
    if inertia_transform == "mid-surface":
        zy_web = cylinder_thickness / 2.0 + centroid_y_web
        zy_base = cylinder_thickness / 2.0 + centroid_y_base
    elif inertia_transform == "top-surface":
        zy_web = centroid_y_web
        zy_base = centroid_y_base
    elif inertia_transform == "percent":
        zy_web = (cylinder_thickness / 2.0 + centroid_y_web) * ringInertiaTransformRatio
        zy_base = (cylinder_thickness / 2.0 + centroid_y_base) * ringInertiaTransformRatio

    moment_of_inertia_web = cross_section.moment_of_inertia_x_web
    moment_of_inertia_base = cross_section.moment_of_inertia_x_base
    torsional_constant_web = cross_section.torsional_constant_web
    torsional_constant_base = cross_section.torsional_constant_base

    extensional = (e_bar_web * area_web + e_bar_base * area_base) / pitch
    bending = (
        (moment_of_inertia_web + area_web * zy_web**2.0) * e_bar_web
        + (moment_of_inertia_base + area_base * zy_base**2.0) * e_bar_base
    ) / pitch
    twisting = (g_bar_web * torsional_constant_web + g_bar_base * torsional_constant_base) / pitch
    coupling = (zy_web * e_bar_web * area_web + zy_base * e_bar_base * area_base) / pitch
    weight = (area_base + area_web) * rho
    return extensional, bending, twisting, coupling, weight, ring_stacking, n_basic_stacking_ring


def getCrossSection(ring_cross_section_type, ply_thickness, ring_stacking, ringHeight, footWidth):

    if ring_cross_section_type.lower() == "t":
        cross_section = TCrossSection(ply_thickness, ring_stacking, ringHeight, footWidth)
    elif ring_cross_section_type.lower() == "rectangle":
        cross_section = RecCrossSection(ply_thickness, ring_stacking)
    else:
        raise NotImplementedError(f'Cross section "{ring_cross_section_type}" is not implemented yet')
    return cross_section


class CrossSection:
    def getAreaMass(self, material, pitch):
        massPerMeter = self.area / 100 / 100 / 100 * material.rho
        massPerArea = massPerMeter / (pitch / 1000)
        return massPerArea


class TCrossSection(CrossSection):
    def __init__(self, h_ply, stack_list, total_height=None, foot_width=None):
        """
        :param h_ply: thickness of a ply
        :param stack_list: stacking as list in [°]. Full stacking for the foot, half stacking of the web
        :param total_height: height of the cross section
        :param foot_width: width of the foot
        """
        h_ply = h_ply if isinstance(h_ply, list) else [h_ply] * len(stack_list)
        h_laminate = float(sum(h_ply))

        """foot stacking thickness"""
        self.foot_thickness = float(h_laminate)

        """web stacking thickness"""
        self.web_thickness = float(2 * self.foot_thickness)

        """web height"""
        self.web_height = float(10 * self.web_thickness) if total_height is None else total_height - self.foot_thickness

        """footwidth"""
        self.foot_width = 50  # float(10 * self.web_thickness) if foot_width is None else foot_width

        """total height"""
        self.total_height = float(self.foot_thickness + self.web_height)

    @property
    def area_web(self):
        return self.web_height * self.web_thickness

    @property
    def area_base(self):
        return self.foot_width * self.foot_thickness

    @property
    def area(self):
        return self.area_base + self.area_web

    @property
    def centroid_y_web(self):
        return self.foot_thickness + self.web_height / 2.0

    @property
    def centroid_y_base(self):
        return self.foot_thickness / 2.0

    @property
    def centroid_x(self):
        return 0.0

    @property
    def centroid_y(self):
        return (self.area_base * self.centroid_y_base + self.area_web * self.centroid_y_web) / (
            self.area_base + self.area_web
        )

    @property
    def moment_of_inertia_x_web(self):
        return (
            self.area_web * self.web_height**2.0 / 12.0 + self.area_web * (self.centroid_y_web - self.centroid_y) ** 2.0
        )

    @property
    def moment_of_inertia_x_base(self):
        return (
            self.area_base * self.foot_thickness**2.0 / 12.0
            + self.area_base * (self.centroid_y_base - self.centroid_y) ** 2.0
        )

    @property
    def moment_of_inertia_y_web(self):
        return self.area_web * self.web_thickness**2.0 / 12.0

    @property
    def moment_of_inertia_y_base(self):
        return self.area_base * self.foot_width**2.0 / 12.0

    @property
    def torsional_constant_web(self):
        # (self._a * self._t ** 3.0 * (0.3333 - 0.105 * self._t / self._a * (1.0 - self._t ** 4.0 / (192.0 * self._a ** 4.0))))
        return 0.3333 * (self.total_height - self.foot_thickness / 2) * self.web_thickness**3

    @property
    def torsional_constant_base(self):
        # (self._b * self._s ** 3.0 * (0.3333 - 0.21 * self._s / self._s * (1.0 - self._s ** 4.0 / (12.0 * self._b ** 4.0))))
        return 0.3333 * self.foot_width * self.foot_thickness**3

    @property
    def display_info(self):
        return f"Cross-section: {self.__class__.__name__}\nA: {self.area_web} + {self.area_base}\nIx: {self.moment_of_inertia_x_web} + {self.moment_of_inertia_x_base}\nJ: {self.torsional_constant_web} + {self.torsional_constant_base}"


class RecCrossSection(CrossSection):
    def __init__(self, h_ply, stack_list, height=None):
        h_ply = h_ply if isinstance(h_ply, list) else [h_ply] * len(stack_list)
        h_laminate = float(sum(h_ply))
        if height:
            self._a = height
        else:
            self._a = float(10 * 2 * h_laminate)
        self._b = float(h_laminate)

    @property
    def area_web(self):
        return self._a * self._b

    @property
    def area_base(self):
        return 0.0

    @property
    def area(self):
        return self.area_web

    def centroid_y_web(self):
        return self._a / 2

    @property
    def centroid_y_base(self):
        return 0.0

    @property
    def centroid_x(self):
        return self._b / 2

    @property
    def centroid_y(self):
        return self._a / 2

    @property
    def moment_of_inertia_x_web(self):
        return self._b * self._a**3 / 12

    @property
    def moment_of_inertia_x_base(self):
        return 0.0

    @property
    def moment_of_inertia_y_web(self):
        return self._b**3 * self._a / 12

    @property
    def moment_of_inertia_y_base(self):
        return 0.0

    @property
    def torsional_constant_web(self):
        return self._a**3 * self._b * (0.3333 - 0.21 * self._a / self._b * (1 - self._a**4 / (12 * self._b**4)))

    @property
    def torsional_constant_base(self):
        return 0.0

    @property
    def display_info(self):
        return f"Cross-section: {self.__class__.__name__}\nA: {self.area_web}\nIx: {self.moment_of_inertia_x_web}\nIy: {self.moment_of_inertia_y_web}\nJ: {self.torsional_constant_web}"


class BucklingConstraintFunction:

    def __init__(self, *args):
        self.usedConstraintFunction = None
        self.args = args  # constants to the problem in usedConstraintFunction

    def __call__(self, x):
        """fun to be called in scipy.optimize.NonlinearConstraint"""
        return self.usedConstraintFunction(x)

    def getCritPressureMetalLocalBuck(self, x):
        liner, material_cylinder, hydrostatic_flag, safety_flag = self.args
        cylinder_thickness, _, nRings = x
        pitch = getPitch(liner.lcyl, nRings)
        critBuckPressure = getCritPressureMetalLocalBuck(
            liner.rCyl, pitch, cylinder_thickness, material_cylinder, hydrostatic_flag, safety_flag
        )
        self.logData(x, critBuckPressure, "Local")
        return critBuckPressure

    def getCritPressureMetalGlobalBuck(self, x):
        liner, material_cylinder, ringParameterDict, hydrostatic_flag, safety_flag = self.args
        cylinder_thickness, ringWebHalfLayerThickness, nRings = x
        ringParameterDict["ringWebHalfLayerThickness"] = ringWebHalfLayerThickness
        critBuckPressure = getCritPressureMetalGlobalBuck(
            liner.rCyl,
            liner.lcyl,
            cylinder_thickness,
            material_cylinder,
            ringParameterDict,
            hydrostatic_flag,
            safety_flag,
        )
        self.logData(x, critBuckPressure, "Global")
        return critBuckPressure

    def logData(self, x, pressure, localOrGlobal):
        optLogger(f"{localOrGlobal} x: {x} buck: {pressure}")


# Example usage

#
#
#
# Cylinder 1 to 5 calculated in Abaqus without Rings:
#
# Cyl_1: 0.00009
# Cyl_2: 0.00180
# Cyl_3: 0.02328
# Cyl_4: 0.11850
# Cyl_5: 0.81424
#


def main():
    if 1:
        from tankoh2.control.control_metal import createDesign
        from tankoh2.control.genericcontrol import parseConfigFile, parseDesignArgs
        from tankoh2.design.metal.material import getMaterialDefinitionMetal
        from tankoh2.geometry.dome import DomeSphere
        from tankoh2.geometry.liner import Liner
        from tankoh2.mechanics.material import MaterialDefinition
        from tankoh2.mechanics.pbucklcritcyl_SP8007 import (
            calculate_designs_for_layups_and_pitches,
            calculate_designs_metal,
            checkStabilityCFRP,
        )

        def getLiner(r=1200, lcyl=1000):
            liner = Liner(DomeSphere(r, 10), lcyl)
            return liner

        paramKwArgs = parseConfigFile("hytazer_smr_iff_2.0bar_final_metal")
        paramKwArgs, _, _ = parseDesignArgs(paramKwArgs, "metal")
        liner = getLiner(paramKwArgs["dcyl"] / 2, paramKwArgs["dcyl"] / 2 * paramKwArgs["lcylByR"])

        material = getMaterialDefinitionMetal(paramKwArgs["materialName"])
        result = createDesign(**paramKwArgs)
        cylinder_thickness = result["wallThickness"]
        result = calculate_designs_metal(
            liner.rCyl,
            liner.length,
            cylinder_thickness,
            material,
            "default_ring",
            None,
            False,
            False,
            paramKwArgs["ringHeight"],
            0.4,  # burst pressure
        )

    def find_first_greater(list1, list2):
        if len(list1) != len(list2):
            raise ValueError("Both lists must be of the same length.")

        for i in range(len(list1)):
            if list1[i] > list2[i]:
                return i

        return None

    if 0:
        # --- Balanced and symmetric laminate with half thickness
        h_ply = 0.125
        radius = 2000.0
        axial_length = 2486.35

        material = dict(E1=120050.0, E2=8460.0, nu12=0.317, G12=3910.0, G13=3910.0, G23=2850.0)
        rho = 1.58e-6
        layup = [
            5.89,
            70.0,
            18.667,
            15.745,
            36.381,
            11.293,
            90.0,
            34.702,
            62.026,
            28.27,
            49.248,
            90.0,
            11.211,
            69.834,
            24.528,
            90.0,
            33.635,
            59.192,
            22.11,
            45.112,
            7.326,
            90.0,
        ]  # 0.3 MPa (SF 2.25)
        layup_complete = balanced_symmetric(layup)  # Create a new function because Tankoh2 is already balanced
        # print("layup_complete: ", layup_complete)
        # print("thickness: ", len(layup_complete) * 0.125)

        # with open('abq_variables.py', 'w') as file:
        #     file.write("# --- Geometry definition\n")
        #     file.write("mdelname = {}\n".format('tank_example'))
        #     file.write("radius = {}\n".format(radius))
        #     file.write("length = {}\n".format(axial_length))
        #     file.write("polar_opening = {}\n".format(250))
        #     file.write("r1_2_d0 = {}\n".format(0.8))
        #     file.write("r2_2_d0 = {}\n".format(0.154))
        #
        #     file.write("# --- Material definition\n")
        #     file.write("name_material = 'comp_example'\n")
        #     file.write("T = {}\n".format(h_ply))
        #     file.write("E11 = {}\n".format(material['E1']))
        #     file.write("E22 = {}\n".format(material['E2']))
        #     file.write("NU12 = {}\n".format(material['nu12']))
        #     file.write("G12 = {}\n".format(material['G12']))
        #     file.write("G13 = {}\n".format(material['G13']))
        #     file.write("G23 = {}\n".format(material['G23']))
        #     file.write("RHO = {}\n".format(material['RHO']))

        # --- New design
        # best_dict_ohne, _ = calculate_critical_pressure(
        #     2500, 2486.35, layup_complete, h_ply, material, None, None, True
        # )

        # Radius changed to 2000 (equal the first geometry I got)
        best_dict_mit, _ = calculate_designs_for_layups_and_pitches(
            2000, 2486.35, layup_complete, h_ply, material, "example_comp", None, True
        )

        # log.info(
        #     "Ohne rings - (best_m, best_n, best_pcr):", best_dict_ohne
        # )  # {'m': 1, 'n': 7, 'p_cr': 0.0201320944109203}
        # log.info("Mit rings - (best_m, best_n, best_pcr):", best_dict_mit)
        import re

        from matplotlib import pyplot as plt

        n_rings = []
        p_local = []
        p_global = []
        r_weight = []
        for key, value in best_dict_mit.items():
            n_ring_str = re.findall(r"\d+", key)
            n_rings.append(int(n_ring_str[0]))
            p_local.append(value["p_cr_local"])
            p_global.append(value["p_cr_global"])
            r_weight.append(value["weight"])

        idx = find_first_greater(p_local, p_global)
        # print("idx: ", idx)
        # print("p_local: ", p_local[idx])
        # print("p_global: ", p_global[idx])

        fig, ax1 = plt.subplots()
        (line1,) = ax1.plot(n_rings, p_local, label="Local buckling pressure")
        (line2,) = ax1.plot(n_rings, p_global, label="Global buckling pressure")
        (marker1,) = ax1.plot(
            [14, 16, 18, 20, 22], [1.7641, 1.9150, 2.0481, 2.1654, 2.2737], marker="o", linestyle="", label="FE"
        )
        ax1.set_ylabel("Critical buckling pressure [MPa]")
        ax1.set_xlabel("Number of rings")

        ax2 = ax1.twinx()
        (line3,) = ax2.plot(n_rings, r_weight, color="r", label="Cylinder weight")
        ax2.set_ylabel("Weight [kg]")

        lines = [line1, line2, line3]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc="upper left")
        ax1.grid(True)
        plt.show()

    if 0:

        if 0:
            data = pd.DataFrame(
                columns=["pCrit", "m_skin", "m_rings", "m_sum", "n_rings", "layerNumber"],
                data=[
                    [0.17217278407033848, 690.4447627765151, 678.4134623934174, 1368.8582251699324, 23, 9],
                    [0.23524044297723617, 718.4480658257934, 678.4134623934174, 1396.8615282192109, 23, 10],
                    [0.24026622641964343, 805.8919445830323, 589.9247499073194, 1395.816694490352, 20, 11],
                    [0.23053664912359143, 859.6540844004578, 501.4360374212215, 1361.0901218216793, 17, 12],
                    [0.2331881134977756, 939.2392366086301, 442.4435624304896, 1381.6827990391198, 15, 13],
                    [0.22519816006002388, 1039.3552137745169, 383.4510874397576, 1422.8063012142745, 13, 14],
                    [0.23981432253287582, 1066.9662818878621, 353.95484994439164, 1420.9211318322536, 12, 15],
                    [0.2501659503948618, 1158.0479032723085, 324.4586124490257, 1482.5065157213342, 11, 16],
                    [0.255936191324185, 1225.3271682496015, 294.9623749536597, 1520.2895432032612, 10, 17],
                    [0.2553560389670731, 1252.8265766174236, 265.46613745829376, 1518.2927140757174, 9, 18],
                    [0.24956061763984946, 1353.0847336087288, 235.96989996292777, 1589.0546335716565, 8, 19],
                ],
            )
            data.index = pd.Series(data["layerNumber"], name="layerNumber")
            subData = data.loc[:, ["m_skin", "m_rings"]]
            ax1 = subData.plot.area()
            subData = data.loc[:, ["n_rings"]]
            ax2 = ax1.twinx()
            ax2 = subData.plot(ax=ax2, color="black")
            ax2.set_ylim([subData.min().min(), subData.max().max() + 8])

            ax1.set_ylabel("Mass Skin + Stiffener [kg]")
            ax2.set_ylabel("Number of rings")
            plt.show()
        else:
            pCrit = [
                0.013759520109615161,
                0.020169146972177074,
                0.026642430648717248,
                0.03340946798950204,
                0.040835385026459246,
                0.04913813782217472,
                0.058522534799577516,
                0.06915340330709509,
                0.0811526798078645,
                0.09460692970821066,
                0.10950458538356266,
                0.12593875832405493,
                0.14386413971393586,
                0.16331791980336763,
                0.18424545362266273,
                0.2066526646906691,
                0.23053664609834956,
                0.2558829353900508,
                0.2826801924439239,
                0.31091942816014495,
                0.34059344548151094,
                0.37169642884052034,
                0.4042236388538218,
            ]

            fig, ax1 = plt.subplots()
            ringCount = np.linspace(1, len(pCrit), num=len(pCrit))
            ax1.plot(ringCount, pCrit, label="critical buckling pressure")
            ax1.set_xlabel("Number of rings")
            # Make the y-axis label, ticks and tick labels match the line color.
            ax1.set_ylabel("Critical buckling pressure [MPa]")
            plt.hlines(y=0.225, xmin=ringCount.min(), xmax=ringCount.max(), linestyle="dashed")
            plt.text(1, 0.225, "Burst Pressure", ha="left", va="bottom")
            plt.legend()  # loc='upper left'
            ax1.grid(True)

            plt.show()


if __name__ == "__main__":
    main()
