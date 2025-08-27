"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import time
from nanosurf.lib.spm import scanhead
import nanosurf
from nanosurf.lib.spm.scanhead import motor_control as mc

class DriveMotorID():
    ALLMOTORS = mc.MotorID(-1, 00, 0)
    ALLAPPROACHMOTORS = mc.MotorID(nanosurf.Spm.SystemMotorID.Approach, 1000, 0.0101)
    APPROACHMOTOR1 =  mc.MotorID(nanosurf.Spm.SystemMotorID.FootA, 1001, 0.0101)
    APPROACHMOTOR2 = mc.MotorID(nanosurf.Spm.SystemMotorID.FootB, 1002, 0.0101)
    APPROACHMOTOR3 = mc.MotorID(nanosurf.Spm.SystemMotorID.FootC, 1003, 0.0101)
    FOCUS = mc.MotorID(nanosurf.Spm.SystemMotorID.Focus, 1004, 0.0056)
    PTE_X = mc.MotorID(nanosurf.Spm.SystemMotorID.PTEX, 1005, 0.0008)
    PTE_Y = mc.MotorID(nanosurf.Spm.SystemMotorID.PTEY, 1006, 0.0008)
    READOUT_X = mc.MotorID(nanosurf.Spm.SystemMotorID.BeamDefX, 1007, 0.0008)
    READOUT_Y = mc.MotorID(nanosurf.Spm.SystemMotorID.BeamDefY, 1008, 0.0008)
    PHOTODIODE_X = mc.MotorID(nanosurf.Spm.SystemMotorID.PhotoDetLateral, 1009, 0.0033)
    PHOTODIODE_Y = mc.MotorID(nanosurf.Spm.SystemMotorID.PhotoDetNormal, 1010, 0.0033)
    LENSEGIMBAL = mc.MotorID(nanosurf.Spm.SystemMotorID.LensGimbal, 1013, 40)
    XAXIS = mc.MotorID(-1, 1011, -1)
    YAXIS = mc.MotorID(-1, 1012, -1)

class DriveAFMScanhead(scanhead.Scanhead):
    def __init__(self, spm: nanosurf.Spm = None, *args, **kargs):
        super().__init__(spm, *args, **kargs)

        self.__pd_adjust_tolerance = 0.005

    def do_connect(self) -> bool:
        if self.spm.is_lowlevel_scripting_enabled():
            self.lu_sensor_ctrl = self.spm.lowlevel.SensorControl(self.spm.lowlevel.SensorControl.Instance.SGLE)
            self.motor_control = mc.MotorControl()
            self.connected = self.motor_control.connect(self.spm)
        else:
            self.logger.error("Lowlevel Scripting interface of spm controller is not enabled.")
        return self.connected

    @property
    def pd_adjust_tolerance(self):
        return self.__pd_adjust_tolerance

    @pd_adjust_tolerance.setter
    def pd_adjust_tolerance(self, val):
        """ """
        self.__pd_adjust_tolerance = val

    def get_motor_control(self) -> mc.MotorControl:
        return self.motor_control

    def start_photo_detector_auto_adjustment(self):
        """ Auto zeroing of photo detector. """
        self.lu_sensor_ctrl.detector_adjustment_tolerance.value = self.pd_adjust_tolerance
        self.lu_sensor_ctrl.start_detector_auto_adjustment()
        time.sleep(self.motor_control.sleep_time_after_motor_command)

    def is_photo_detector_auto_adjustment_running(self) -> bool:
        """ """
        running = self.lu_sensor_ctrl.detector_auto_adjustment_status.value != 0.0
        return running

    def stop_photo_detector_auto_adjustment(self):
        self.lu_sensor_ctrl.user_abort()

    def do_photo_detector_auto_adjustment(self, timeout: float = 60.0) -> bool:
        """Function to start the AutoZeroing and wait until terminated (uses the three other functions above).
        If the adjustment terminated not successfully after 30 seconds it is stopped and return value is false.
        """
        self.logger.info("Start Centering Photodiode")
        self.start_photo_detector_auto_adjustment()

        success = True
        start_time = time.time()
        while self.is_photo_detector_auto_adjustment_running():
            if (time.time() - start_time) > timeout:
                self.stop_photo_detector_auto_adjustment()
                self.logger.error("Centering of Photodiode Failed")
                success = False
                break
            time.sleep(0.5)
        self.stop_photo_detector_auto_adjustment()
        self.motor_control.stop_all_motors()
        if success:
            self.logger.info("Centering of Photodiode Succeeded")
        return success

    def do_move_lasers_to_zero(self) -> bool:
        """ Move both lasers to zero position
        """
        motors = DriveMotorID()
        laser_motors = [motors.PTE_X, motors.PTE_Y, motors.READOUT_X, motors.READOUT_Y]
        done = self.motor_control.do_move_absolute(laser_motors , [0.0 for i in laser_motors])

        if done:
            self.logger.debug("Lasers are moved to zero position without referencing")
        else:
            self.logger.error("Error or timeout while moving lasers to zero position")
        return done

    def do_move_all_optics_to_zero(self) -> bool:
        """ Centers all the optical adjustment motors:
            Lasers and photodiode axis are centered.
            The lensegimbal and the focus are set to the position for air
        """
        motors = DriveMotorID()
        optics_motors = [
            motors.PTE_X, motors.PTE_Y, motors.READOUT_X, motors.READOUT_Y,
            motors.PHOTODIODE_X, motors.PHOTODIODE_Y,
            motors.LENSEGIMBAL, motors.FOCUS
        ]
        done = self.motor_control.do_move_absolute(optics_motors, [0.0 for i in optics_motors])

        if done:
            self.logger.debug("All optics motors are moved to zero position without referencing")
        else:
            self.logger.error("Error or timeout while moving motors to zero position")
        return done

    def do_move_all_optics_to_initial_position(self) -> bool:
        """ Centers all the optical adjustment motors:
            Lasers and photodiode axis are centered.
            The lensegimbal and the focus are set to the position for air
        """
        done = True
        motors = DriveMotorID()
        motors_for_centering = [
            motors.PTE_X, motors.PTE_Y, motors.READOUT_X, motors.READOUT_Y,
            motors.PHOTODIODE_X, motors.PHOTODIODE_Y
        ]
        motors_to_position = [motors.LENSEGIMBAL, motors.FOCUS]
        move_position_list = [32, 0.0028] # 32 degrees should be vertically aligned
        if done:
            done &= self.motor_control.do_motor_reference_and_center(motors_for_centering)
        if done:
            done &= self.motor_control.do_motor_referencing(motors_to_position)
        if done:
            done &= self.motor_control.do_move_relative(motors_to_position, move_position_list)
        if done:
            self.motor_control.set_motor_zero_position(motors_for_centering + motors_to_position)

        if done:
            self.logger.debug("All optics motors are initial positionreferenced, centered and zeroed")
        else:
            self.logger.error("Error or timeout while moving motors to initial position")
        return done

    def do_move_all_feet_motors_to_full_range_then_center(self) -> bool:
        """ Move feet motors to full extension and full retraction and then to mid position
        """
        done = True
        all_approach_motor_id = DriveMotorID().ALLAPPROACHMOTORS
        if done:
            done &= self.motor_control.do_motor_referencing(all_approach_motor_id)
        if done:
            done &= self.motor_control.do_move_relative(all_approach_motor_id, 1) # We move full range (just large enough number and wait until motor stopped)
        if done:
            mid_range = self.motor_control.get_motor_full_range(all_approach_motor_id) / 2.0
            done &= self.motor_control.do_move_relative(all_approach_motor_id, -mid_range)
        if done:
            self.logger.debug("All approach feeds are moved to center position")
        else:
            self.logger.error("Error or timeout while moving approach motors to center position")
        return done

    def do_reference_and_move_back_lasers(self) -> bool:
        """ Reference and Move Back all laser motors (they should overlay optically, during the scanhead calibration, the lasers should be both
        in the optical center """
        done = True
        motors = DriveMotorID()
        motors_for_centering = [motors.PTE_X, motors.PTE_Y, motors.READOUT_X, motors.READOUT_Y]
        done &= self.motor_control.do_reference_and_move_back(motors_for_centering)
        return done