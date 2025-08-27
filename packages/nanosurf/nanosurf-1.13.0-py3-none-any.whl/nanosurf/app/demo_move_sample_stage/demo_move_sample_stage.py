# This is a script for controlling the nanosurf sample stage
# 
# Author: Hans Gunstheimer, Oct 2022

#################################################################################################################
#                                                                                                               #
#                                           Imports and definitions                                             #
#                                                                                                               #
#################################################################################################################
# import nanosurf library use pip install nanosurf to install
import time
import nanosurf as nsf

AXIS_X_ID = 0
AXIS_Y_ID = 1

#################################################################################################################
#                                                                                                               #
#                                           Commands for moving the stage                                       #
#                                                                                                               #
#################################################################################################################
def stop_stage():
    #%% Stop stage!
    stage.stop()
    print("Stage stopped!")

def print_stage_information():
    #%% Do a quick check:
    #   Check if stage is connected and referenced:
    print(f"Is there a stage instance available? {stage.HasInstance}")
    print(f"Is stage referenced? {stage.IsReferenced}")

    #   Get axis names and units:
    print(f"Axis 0: Name='{stage.GetAxisName(AXIS_X_ID)}' unit: {stage.GetAxisUnit(AXIS_X_ID)}")
    print(f"Axis 1: Name='{stage.GetAxisName(AXIS_Y_ID)}' unit: {stage.GetAxisUnit(AXIS_Y_ID)}")
    
    #   Get stage status:
    current_state = stage.GetState
    if current_state == spm.StageState.IdleUnreferenced:
        print("Stage state: Idle unreferenced")
    elif current_state == spm.StageState.Idle:
        print("Stage state: Idle referenced")
    elif current_state == spm.StageState.Moving:
        print("Stage state: Moving")
    else: print(f"Stage state: unknown {current_state}")

    #   Get current stage position and speed:
    pos_x = stage.GetAxisPosition(AXIS_X_ID)
    print(f"Current position of stage {stage.GetAxisName(AXIS_X_ID)}: {nsf.sci_val.convert.to_string(pos_x, stage.GetAxisUnit(AXIS_X_ID))}")
    pos_y = stage.GetAxisPosition(AXIS_Y_ID)
    print(f"Current position of stage {stage.GetAxisName(AXIS_Y_ID)}: {nsf.sci_val.convert.to_string(pos_y, stage.GetAxisUnit(AXIS_Y_ID))}")
    print(f"Stage speed: {stage.GetSpeedPercent}%")
    
    #   Get range of stage and zero position:
    range_x = stage.GetAxisRange(AXIS_X_ID)
    zero_x = stage.GetCurrentAxisZeroPosition(AXIS_X_ID)
    print(f"Total axis range of {stage.GetAxisName(AXIS_X_ID)} is: {nsf.sci_val.convert.to_string(range_x, stage.GetAxisUnit(AXIS_X_ID))}")
    print(f"Zero position of {stage.GetAxisName(AXIS_X_ID)} is: {nsf.sci_val.convert.to_string(zero_x, stage.GetAxisUnit(AXIS_X_ID))}")
    print(f"{stage.GetAxisName(AXIS_X_ID)} can move +/-: {nsf.sci_val.convert.to_string(range_x/2.0, stage.GetAxisUnit(AXIS_X_ID))}")
    
    range_y = stage.GetAxisRange(AXIS_Y_ID)
    zero_y = stage.GetCurrentAxisZeroPosition(AXIS_Y_ID)
    print(f"Total axis range of {stage.GetAxisName(AXIS_Y_ID)} is: {nsf.sci_val.convert.to_string(range_y, stage.GetAxisUnit(AXIS_Y_ID))}")
    print(f"Zero position of {stage.GetAxisName(AXIS_Y_ID)} is: {nsf.sci_val.convert.to_string(zero_y, stage.GetAxisUnit(AXIS_Y_ID))}")
    print(f"{stage.GetAxisName(AXIS_Y_ID)} can move +/-: {nsf.sci_val.convert.to_string(range_y/2.0, stage.GetAxisUnit(AXIS_Y_ID))}")
    
def do_reference_search():
    #%% Do a reference search. Lift your cantilever to a save position before and take care that the stage can move over
    #   the complete range. Make sure to avoid any damage through physical contact. Performing this step is recommended before starting
    #   any experiment. Reference search might take a couple of seconds. Final position of stage is set to the center. Reference gets lost
    #   if stage is turned off.
    stage.ReferenceSearch()

def get_current_position():
    #%% Get the current stage position in um:
    pos_x = stage.GetAxisPosition(AXIS_X_ID)
    pos_y = stage.GetAxisPosition(AXIS_Y_ID)
    print(f"Current x-position: {nsf.sci_val.convert.to_string(pos_x, stage.GetAxisUnit(AXIS_X_ID))}")
    print(f"Current y-position: {nsf.sci_val.convert.to_string(pos_y, stage.GetAxisUnit(AXIS_Y_ID))}")

def set_current_pos_to_zero():
    #%% Set current position to zero
    stage.SetAxisZero(AXIS_X_ID)
    print(str(stage.GetAxisName(AXIS_X_ID))+" was set to zero")
    stage.SetAxisZero(AXIS_Y_ID)
    print(str(stage.GetAxisName(AXIS_Y_ID))+" was set to zero")

def set_stage_speed(stage_speed_percent:float):
    if (stage_speed_percent >= 0) and (stage_speed_percent <= 100):
        stage.SetSpeedPercent(stage_speed_percent)
        print("Stage speed was set to "+str(stage.GetSpeedPercent)+"%")
    else: print("Set a stage speed value between 0% and 100%")

def is_stage_moving() -> bool:
    """ check if stage is moving:"""
    # %% 
    return stage.GetState == spm.StageState.Moving

def move_stage_xy(x_movement:float, y_movement:float, relative_movement_to_current_pos:bool = True):
    #%% move stage in x
    stage.AppendToMoveTransaction(AXIS_X_ID, x_movement, relative_movement_to_current_pos)
    stage.AppendToMoveTransaction(AXIS_Y_ID, y_movement, relative_movement_to_current_pos)
    stage.CommitMoveTransaction()
    stage.ClearMoveTransaction()
    while stage.GetState == spm.StageState.Moving:
        time.sleep(0.05)
    print(f"New x-position: {nsf.sci_val.convert.to_string(stage.GetAxisPosition(AXIS_X_ID), stage.GetAxisUnit(AXIS_X_ID))}")
    print(f"New y-position: {nsf.sci_val.convert.to_string(stage.GetAxisPosition(AXIS_Y_ID), stage.GetAxisUnit(AXIS_Y_ID))}")

def lock_stage(lock_stage:bool = True):
    """ Lock stage for measurements """
    if lock_stage:
        # %% Lock stage for measurements:
        stage.Lock()
        print("Stage is locked.")
    else:
        # %% Unlock stage to move:
        stage.Unlock()
        print("Stage is unlocked.")

def unlock_stage():
    """ Unlock stage to move: """
    # %% Unlock stage to move:
    stage.Unlock()
    print("Stage is unlocked.")

# %% connect to controller and stage:
print("Connecting to a running Nanosurf Control software...")
spm = nsf.SPM() # Depending on the software version, this could be nanosurf.C3000(), or nanosurf.CoreAFM(), etc.
if not spm.is_connected():
    print("Controller could not be found. Check if controller software is running and connected with controller.")    
    exit()
if not spm.is_scripting_enabled():
    print("Sorry scripting is not activated on this controller.")
    exit()

# make a shortcut to the application object and stage, to make subsequent code shorter:
# Load stage application:
application = spm.application
stage = application.Stage

stop_stage()
print_stage_information()

