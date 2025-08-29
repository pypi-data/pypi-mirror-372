import json
import typing as t
from datetime import datetime, timedelta

from prefect import flow, get_run_logger, task
from prefect.cache_policies import NO_CACHE
from punchbowl.level1.flow import level1_early_core_flow, level1_late_core_flow
from sqlalchemy import func, text
from sqlalchemy.orm import aliased

from punchpipe import __version__
from punchpipe.control import cache_layer
from punchpipe.control.db import File, FileRelationship, Flow
from punchpipe.control.processor import generic_process_flow_logic
from punchpipe.control.scheduler import generic_scheduler_flow_logic
from punchpipe.flows.util import file_name_to_full_path

SCIENCE_LEVEL0_TYPE_CODES = ["PM", "PZ", "PP", "CR"]
SCIENCE_LEVEL1_LATE_INPUT_TYPE_CODES = ["XM", "XZ", "XP", "XR"]
SCIENCE_LEVEL1_LATE_OUTPUT_TYPE_CODES = ["PM", "PZ", "PP", "CR"]
SCIENCE_LEVEL1_QUICK_INPUT_TYPE_CODES = ["XR"]
SCIENCE_LEVEL1_QUICK_OUTPUT_TYPE_CODES = ["QR"]

@task(cache_policy=NO_CACHE)
def level1_early_query_ready_files(session, pipeline_config: dict, reference_time=None, max_n=9e99):
    logger = get_run_logger()
    ready = (session.query(File).filter(File.file_type.in_(SCIENCE_LEVEL0_TYPE_CODES))
                                .filter(File.state == "created")
                                .filter(File.level == "0")
                                .order_by(File.date_obs.desc()).all())

    actually_ready = []
    for f in ready:
        if get_quartic_model_path(f, pipeline_config, session=session) is None:
            logger.info(f"Missing quartic model for {f.filename()}")
            continue
        if get_vignetting_function_path(f, pipeline_config, session=session) is None:
            logger.info(f"Missing vignetting function for {f.filename()}")
            continue
        actually_ready.append([f])
        if len(actually_ready) >= max_n:
            break
    return actually_ready

def get_distortion_path(level0_file, pipeline_config: dict, session=None, reference_time=None):
    best_function = (session.query(File)
                     .filter(File.file_type == "DS")
                     .filter(File.observatory == level0_file.observatory)
                     .where(File.date_obs <= level0_file.date_obs)
                     .order_by(File.date_obs.desc()).first())
    return best_function

def get_vignetting_function_path(level0_file, pipeline_config: dict, session=None, reference_time=None):
    corresponding_vignetting_function_type = {"PM": "GM",
                                              "PZ": "GZ",
                                              "PP": "GP",
                                              "CR": "GR"}
    vignetting_function_type = corresponding_vignetting_function_type[level0_file.file_type]
    best_function = (session.query(File)
                     .filter(File.file_type == vignetting_function_type)
                     .filter(File.observatory == level0_file.observatory)
                     .where(File.date_obs <= level0_file.date_obs)
                     .order_by(File.date_obs.desc()).first())
    return best_function


def get_psf_model_path(level0_file, pipeline_config: dict, session=None, reference_time=None) -> str:
    corresponding_psf_model_type = {"PM": "RM",
                                    "PZ": "RZ",
                                    "PP": "RP",
                                    "CR": "RC",
                                    "XM": "RM",
                                    "XZ": "RZ",
                                    "XP": "RP",
                                    "XR": "RC"}
    psf_model_type = corresponding_psf_model_type[level0_file.file_type]
    # TODO - Turn this back on once fine tuned for NFI
    if level0_file.observatory == "4":
        return ""
    best_model = (session.query(File)
                  .filter(File.file_type == psf_model_type)
                  .filter(File.observatory == level0_file.observatory)
                  .where(File.date_obs <= level0_file.date_obs)
                  .order_by(File.date_obs.desc()).first())
    return best_model.filename()


STRAY_LIGHT_CORRESPONDING_TYPES = {"PM": "SM",
                                   "PZ": "SZ",
                                   "PP": "SP",
                                   "CR": "SR",
                                   "XM": "SM",
                                   "XZ": "SZ",
                                   "XP": "SP",
                                   "XR": "SR"}


def get_two_closest_stray_light(level0_file, session=None, max_distance: timedelta = None):
    model_type = STRAY_LIGHT_CORRESPONDING_TYPES[level0_file.file_type]
    best_models = (session.query(File, dt := func.abs(func.timestampdiff(
                        text("second"), File.date_obs, level0_file.date_obs)))
                  .filter(File.file_type == model_type)
                  .filter(File.observatory == level0_file.observatory)
                  .filter(File.state == "created"))
    if max_distance:
        best_models = best_models.filter(dt < max_distance.total_seconds())
    best_models = best_models.order_by(dt.asc()).limit(2).all()
    if len(best_models) < 2:
        return None, None
    # Drop the dt values
    best_models = [x[0] for x in best_models]
    if best_models[1].date_obs < best_models[0].date_obs:
        best_models = best_models[::-1]
    return best_models


def get_two_best_stray_light(level0_file, session=None):
    model_type = STRAY_LIGHT_CORRESPONDING_TYPES[level0_file.file_type]
    before_model = (session.query(File)
                    .filter(File.file_type == model_type)
                    .filter(File.observatory == level0_file.observatory)
                    .filter(File.level == '1')
                    .filter(File.date_obs < level0_file.date_obs)
                    .order_by(File.date_obs.desc()).first())
    after_model = (session.query(File)
                   .filter(File.file_type == model_type)
                   .filter(File.observatory == level0_file.observatory)
                   .filter(File.level == '1')
                   .filter(File.date_obs > level0_file.date_obs)
                   .order_by(File.date_obs.asc()).first())
    if before_model is None or after_model is None:
        # We're waiting for the scheduler to fill in here and tell us what's what
        return None, None
    elif before_model.state == "created" and after_model.state == "created":
        # Good to go!
        return before_model, after_model
    elif before_model.state == "impossible" or after_model.state == "impossible":
        # Flexible mode
        dt = func.abs(func.timestampdiff(text("second"), File.date_obs, level0_file.date_obs))
        models = (session.query(File, dt)
                  .filter(File.file_type == model_type)
                  .filter(File.observatory == level0_file.observatory)
                  .filter(File.level == '1')
                  .filter(File.state != "impossible")
                  .order_by(dt.asc())
                  .limit(2).all())
        # Drop the dt values
        before_model, after_model = [x[0] for x in models]
        if before_model.state == "created" and after_model.state == "created":
            # Good to go!
            return before_model, after_model
        else:
            # Wait for files to generate
            return None, None
    # If we're here, we're waiting for at least one model to generate, but we do expect it to do so
    return None, None


def get_quartic_model_path(level0_file, pipeline_config: dict, session=None, reference_time=None):
    best_model = (session.query(File)
                  .filter(File.file_type == 'FQ')
                  .filter(File.observatory == level0_file.observatory)
                  .where(File.date_obs <= level0_file.date_obs)
                  .order_by(File.date_obs.desc()).first())
    return best_model


def get_mask_file(level0_file, pipeline_config: dict, session=None, reference_time=None):
    best_model = (session.query(File)
                  .filter(File.file_type == 'MS')
                  .filter(File.observatory == level0_file.observatory)
                  .where(File.date_obs <= level0_file.date_obs)
                  .order_by(File.date_obs.desc()).first())
    return best_model


def get_ccd_parameters(level0_file, pipeline_config: dict, session=None):
    gain_bottom, gain_top = pipeline_config['ccd_gain'][int(level0_file.observatory)]
    return {"gain_bottom": gain_bottom, "gain_top": gain_top}


def level1_early_construct_flow_info(level0_files: list[File], level1_files: list[File],
                               pipeline_config: dict, session=None, reference_time=None):
    flow_type = "level1_early"
    state = "planned"
    creation_time = datetime.now()
    priority = pipeline_config["flows"][flow_type]["priority"]["initial"]

    best_vignetting_function = get_vignetting_function_path(level0_files[0], pipeline_config, session=session)
    best_quartic_model = get_quartic_model_path(level0_files[0], pipeline_config, session=session)
    ccd_parameters = get_ccd_parameters(level0_files[0], pipeline_config, session=session)
    mask_function = get_mask_file(level0_files[0], pipeline_config, session=session)

    call_data = json.dumps(
        {
            "input_data": [level0_file.filename() for level0_file in level0_files],
            "vignetting_function_path": best_vignetting_function.filename(),
            "quartic_coefficient_path": best_quartic_model.filename(),
            "gain_bottom": ccd_parameters['gain_bottom'],
            "gain_top": ccd_parameters['gain_top'],
            "mask_path": mask_function.filename().replace('.fits', '.bin'),
        }
    )
    return Flow(
        flow_type=flow_type,
        flow_level="1",
        state=state,
        creation_time=creation_time,
        priority=priority,
        call_data=call_data,
    )


def level1_early_construct_file_info(level0_files: t.List[File], pipeline_config: dict, reference_time=None) -> t.List[File]:
    files = []
    files.append(File(
            level="1",
            file_type='X' + level0_files[0].file_type[1:],
            observatory=level0_files[0].observatory,
            file_version=pipeline_config["file_version"],
            software_version=__version__,
            date_obs=level0_files[0].date_obs,
            polarization=level0_files[0].polarization,
            outlier=level0_files[0].outlier,
            state="planned",
        ))
    return files


@flow
def level1_early_scheduler_flow(pipeline_config_path=None, session=None, reference_time=None):
    generic_scheduler_flow_logic(
        level1_early_query_ready_files,
        level1_early_construct_file_info,
        level1_early_construct_flow_info,
        pipeline_config_path,
        reference_time=reference_time,
        session=session,
    )


def level1_early_call_data_processor(call_data: dict, pipeline_config, session=None) -> dict:
    for key in ['input_data', 'quartic_coefficient_path', 'vignetting_function_path', 'mask_path']:
        call_data[key] = file_name_to_full_path(call_data[key], pipeline_config['root'])

    call_data['quartic_coefficient_path'] = cache_layer.quartic_coefficients.wrap_if_appropriate(
        call_data['quartic_coefficient_path'])
    call_data['vignetting_function_path'] = cache_layer.vignetting_function.wrap_if_appropriate(
        call_data['vignetting_function_path'])
    # Anything more than 16 doesn't offer any real benefit, and the default of n_cpu on punch190 is actually slower than
    # 16! Here we choose less to have less spiky CPU usage to play better with other flows.
    call_data['max_workers'] = 2
    return call_data


@flow
def level1_early_process_flow(flow_id: int, pipeline_config_path=None, session=None):
    generic_process_flow_logic(flow_id, level1_early_core_flow, pipeline_config_path, session=session,
                               call_data_processor=level1_early_call_data_processor)


@task(cache_policy=NO_CACHE)
def level1_late_query_ready_files(session, pipeline_config: dict, reference_time=None, max_n=9e99):
    logger = get_run_logger()
    parent = aliased(File)
    child = aliased(File)
    child_exists_subquery = (session.query(parent)
                             .join(FileRelationship, FileRelationship.parent == parent.file_id)
                             .join(child, FileRelationship.child == child.file_id)
                             .filter(parent.file_id == File.file_id)
                             .filter(child.file_type.in_(SCIENCE_LEVEL1_LATE_OUTPUT_TYPE_CODES))
                             .exists())
    ready = (session.query(File)
             .filter(File.file_type.in_(SCIENCE_LEVEL1_LATE_INPUT_TYPE_CODES))
             .filter(File.level == "1")
             .filter(File.state.in_(["created", "progressed"]))
             .filter(~child_exists_subquery)
             .order_by(File.date_obs.desc()).all())

    actually_ready = []
    for f in ready:
        if list(get_two_best_stray_light(f, session=session)) == [None, None]:
            logger.info(f"Waiting for stray light models for {f.filename()}")
            continue
        if get_distortion_path(f, pipeline_config, session=session) is None:
            logger.info(f"Missing distortion function for {f.filename()}")
            continue
        if get_psf_model_path(f, pipeline_config, session=session) is None:
            logger.info(f"Missing PSF for {f.filename()}")
            continue
        actually_ready.append([f])
        if len(actually_ready) >= max_n:
            break
    return actually_ready


def level1_late_construct_flow_info(input_files: list[File], output_files: list[File],
                                    pipeline_config: dict, session=None, reference_time=None):
    flow_type = "level1_late"
    state = "planned"
    creation_time = datetime.now()
    priority = pipeline_config["flows"][flow_type]["priority"]["initial"]

    best_psf_model = get_psf_model_path(input_files[0], pipeline_config, session=session)
    best_distortion = get_distortion_path(input_files[0], pipeline_config, session=session)
    stray_light_before, stray_light_after = get_two_best_stray_light(input_files[0], session=session)
    mask_function = get_mask_file(input_files[0], pipeline_config, session=session)

    call_data = json.dumps(
        {
            "input_data": [input_file.filename() for input_file in input_files],
            "psf_model_path": best_psf_model,
            "distortion_path": best_distortion.filename(),
            "stray_light_before_path": stray_light_before.filename() if stray_light_before else None,
            "stray_light_after_path": stray_light_after.filename() if stray_light_after else None,
            "mask_path": mask_function.filename().replace('.fits', '.bin'),
            "output_as_Q_file": False,
        }
    )
    return Flow(
        flow_type=flow_type,
        flow_level="1",
        state=state,
        creation_time=creation_time,
        priority=priority,
        call_data=call_data,
    )


def level1_late_construct_file_info(input_files: t.List[File], pipeline_config: dict, reference_time=None) -> t.List[File]:
    prefix = 'C' if input_files[0].polarization == 'C' else 'P'
    return [
        File(
            level="1",
            file_type=prefix + input_files[0].file_type[1:],
            observatory=input_files[0].observatory,
            file_version=pipeline_config["file_version"],
            software_version=__version__,
            date_obs=input_files[0].date_obs,
            polarization=input_files[0].polarization,
            outlier=input_files[0].outlier,
            state="planned",
        )
    ]


@flow
def level1_late_scheduler_flow(pipeline_config_path=None, session=None, reference_time=None):
    generic_scheduler_flow_logic(
        level1_late_query_ready_files,
        level1_late_construct_file_info,
        level1_late_construct_flow_info,
        pipeline_config_path,
        reference_time=reference_time,
        session=session,
    )


def level1_late_call_data_processor(call_data: dict, pipeline_config, session=None) -> dict:
    for key in ['input_data', 'mask_path', 'stray_light_before_path', 'stray_light_after_path', 'distortion_path']:
        call_data[key] = file_name_to_full_path(call_data[key], pipeline_config['root'])

    # TODO: this is a hack to skip NFI PSF. Remove!
    if call_data['psf_model_path'] == "":
        call_data['psf_model_path'] = None
    else:
        call_data['psf_model_path'] = file_name_to_full_path(call_data['psf_model_path'], pipeline_config['root'])
        call_data['psf_model_path'] = cache_layer.psf.wrap_if_appropriate(call_data['psf_model_path'])

    # Anything more than 16 doesn't offer any real benefit, and the default of n_cpu on punch190 is actually slower than
    # 16! Here we choose less to have less spiky CPU usage to play better with other flows.
    call_data['max_workers'] = 2
    return call_data


@flow
def level1_late_process_flow(flow_id: int, pipeline_config_path=None, session=None):
    generic_process_flow_logic(flow_id, level1_late_core_flow, pipeline_config_path, session=session,
                               call_data_processor=level1_late_call_data_processor)


@task(cache_policy=NO_CACHE)
def level1_quick_query_ready_files(session, pipeline_config: dict, reference_time=None, max_n=9e99):
    logger = get_run_logger()
    parent = aliased(File)
    child = aliased(File)
    child_exists_subquery = (session.query(parent)
                             .join(FileRelationship, FileRelationship.parent == parent.file_id)
                             .join(child, FileRelationship.child == child.file_id)
                             .filter(parent.file_id == File.file_id)
                             .filter(child.file_type.in_(SCIENCE_LEVEL1_QUICK_OUTPUT_TYPE_CODES))
                             .exists())
    ready = (session.query(File)
             .filter(File.file_type.in_(SCIENCE_LEVEL1_QUICK_INPUT_TYPE_CODES))
             .filter(File.level == "1")
             .filter(File.state.in_(["created", "progressed"]))
             .filter(~child_exists_subquery)
             .order_by(File.date_obs.desc()).all())

    actually_ready = []
    for f in ready:
        if list(get_two_closest_stray_light(f, session=session)) == [None, None]:
            logger.info(f"Waiting for stray light models for {f.filename()}")
            continue
        if get_distortion_path(f, pipeline_config, session=session) is None:
            logger.info(f"Missing distortion function for {f.filename()}")
            continue
        if get_psf_model_path(f, pipeline_config, session=session) is None:
            logger.info(f"Missing PSF for {f.filename()}")
            continue
        actually_ready.append([f])
        if len(actually_ready) >= max_n:
            break
    return actually_ready


def level1_quick_construct_flow_info(input_files: list[File], output_files: list[File],
                                    pipeline_config: dict, session=None, reference_time=None):
    flow_type = "level1_quick"
    state = "planned"
    creation_time = datetime.now()
    priority = pipeline_config["flows"][flow_type]["priority"]["initial"]

    best_psf_model = get_psf_model_path(input_files[0], pipeline_config, session=session)
    best_distortion = get_distortion_path(input_files[0], pipeline_config, session=session)
    stray_light_before, stray_light_after = get_two_closest_stray_light(input_files[0], session=session)
    mask_function = get_mask_file(input_files[0], pipeline_config, session=session)

    call_data = json.dumps(
        {
            "input_data": [input_file.filename() for input_file in input_files],
            "psf_model_path": best_psf_model,
            "distortion_path": best_distortion.filename(),
            "stray_light_before_path": stray_light_before.filename() if stray_light_before else None,
            "stray_light_after_path": stray_light_after.filename() if stray_light_after else None,
            "mask_path": mask_function.filename().replace('.fits', '.bin'),
            "output_as_Q_file": True,
        }
    )
    return Flow(
        flow_type=flow_type,
        flow_level="1",
        state=state,
        creation_time=creation_time,
        priority=priority,
        call_data=call_data,
    )


def level1_quick_construct_file_info(input_files: t.List[File], pipeline_config: dict, reference_time=None) -> t.List[File]:
    return [
        File(
            level="1",
            file_type="Q" + input_files[0].file_type[1:],
            observatory=input_files[0].observatory,
            file_version=pipeline_config["file_version"],
            software_version=__version__,
            date_obs=input_files[0].date_obs,
            polarization=input_files[0].polarization,
            outlier=input_files[0].outlier,
            state="planned",
        )
    ]


@flow
def level1_quick_scheduler_flow(pipeline_config_path=None, session=None, reference_time=None):
    generic_scheduler_flow_logic(
        level1_quick_query_ready_files,
        level1_quick_construct_file_info,
        level1_quick_construct_flow_info,
        pipeline_config_path,
        reference_time=reference_time,
        session=session,
    )


def level1_quick_call_data_processor(call_data: dict, pipeline_config, session=None) -> dict:
    for key in ['input_data', 'mask_path', 'stray_light_before_path', 'stray_light_after_path', 'distortion_path']:
        call_data[key] = file_name_to_full_path(call_data[key], pipeline_config['root'])

    # TODO: this is a hack to skip NFI PSF. Remove!
    if call_data['psf_model_path'] == "":
        call_data['psf_model_path'] = None
    else:
        call_data['psf_model_path'] = file_name_to_full_path(call_data['psf_model_path'], pipeline_config['root'])
        call_data['psf_model_path'] = cache_layer.psf.wrap_if_appropriate(call_data['psf_model_path'])

    # Anything more than 16 doesn't offer any real benefit, and the default of n_cpu on punch190 is actually slower than
    # 16! Here we choose less to have less spiky CPU usage to play better with other flows.
    call_data['max_workers'] = 2
    return call_data


@flow
def level1_quick_process_flow(flow_id: int, pipeline_config_path=None, session=None):
    generic_process_flow_logic(flow_id, level1_late_core_flow, pipeline_config_path, session=session,
                               call_data_processor=level1_quick_call_data_processor)
