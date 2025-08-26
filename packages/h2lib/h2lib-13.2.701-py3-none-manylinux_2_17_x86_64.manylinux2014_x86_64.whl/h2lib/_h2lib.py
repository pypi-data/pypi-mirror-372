from contextlib import contextmanager
from h2lib.dll_wrapper import DLLWrapper
from h2lib.h2lib_signatures import H2LibSignatures
import os
import sys

from multiclass_interface.multiprocess_interface import MultiProcessClassInterface, ProcessClass
import numpy as np
from pathlib import Path
from h2lib.distributed_sections import H2Lib_DistributedSections

_ERROR_CODES = {
    1: ValueError("WRONG_NUMBER_OF_COLUMNS"),
    2: ValueError("MAIN_BODY_NOT_FOUND"),
    3: NotImplementedError(),
    4: RuntimeError("STRUCTURE_IS_CONFIDENTIAL"),
    5: IndexError("BODY_DOES_NOT_EXIST"),
    6: IndexError("ELEMENT_DOES_NOT_EXIST"),
    7: ValueError("WRONG_NUMBER_OF_BODIES"),
    100: RuntimeError("STATIC_SOLVER_DID_NOT_CONVERGE"),
    101: RuntimeError("STATIC_SOLVER_NOT_INITIALIZED"),
    300: ValueError("TOO_FEW_SECTIONS_IN_C2DEF"),
    301: ValueError("BEAM_TOO_SHORT"),
    302: ValueError("DIFFERENT_NSEC"),
    500: ValueError("RELATIVE_ROTATION_NOT_FOUND"),
    700: RuntimeError("SYSTEM_NOT_LINEARIZED"),
    701: RuntimeError("SYSTEM_EIGENANALYSIS_NOT_DONE"),
    702: ValueError("TOO_MANY_MODES_REQUESTED"),
    703: ValueError("WRONG_TOTAL_DOF"),
    704: ValueError("WRONG_REDUCED_DOF")
}


class H2LibThread(DLLWrapper, H2Lib_DistributedSections, H2LibSignatures):
    _model_path = '.'
    _aero_sections_data_shape = {}

    def __init__(self, suppress_output=True, filename=None, cwd='.'):
        if filename is None:
            if os.name == 'nt':
                filename = os.path.dirname(__file__) + '/HAWC2Lib.dll'
            else:
                filename = os.path.dirname(__file__) + '/HAWC2Lib.so'  # pragma: no cover
        # doubles the speed of single instances and 2N of N instances on linux
        os.environ['MKL_THREADING_LAYER'] = 'sequential'
        filename = os.path.abspath(filename)
        for f in [sys.base_prefix, sys.prefix]:
            if os.path.isdir(os.path.join(f, 'Library/bin')):
                os.add_dll_directory(os.path.join(f, 'Library/bin'))
        DLLWrapper.__init__(self, filename, cwd=cwd, cdecl=True)
        self.stop_on_error(False)
        self.suppress_output = suppress_output
        self._initialized = False
        self.time = 0

    @property
    def model_path(self):
        return self._model_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._initialized:
            self.write_output()
            self.finalize()
        DLLWrapper.close(self)
        return "closed h2lib"

    def getState(self):
        return H2LibSignatures.getState(self, restype=np.int32)[1]

    def work(self, time):
        """Return number of loops"""
        return H2LibSignatures.work(self, np.float64(time), restype=np.int64)[1]

    def loop(self, N):
        """Return time to compute N loops"""
        return H2LibSignatures.loop(self, int(N), restype=np.float64)[1]

    def get_version(self):
        s = " " * 255
        return H2LibSignatures.get_version(self, s)[0][0].strip()

    def stop_on_error(self, flag):
        """
        Control if HAWC2 will terminate the execution upon encountering an error. The default HAWC2 behavior is to stop.

        Parameters
        ----------
        flag : bool
            If set to `True` an error will cause HAWC2 to terminate the execution with status code 1.
            If set to `False` HAWC2 will still print a log message but not stop.

        Returns
        -------
        None.

        """
        H2LibSignatures.stop_on_error(self, bool(flag))

    def get_wind_speed(self, pos_g):
        return self.get_lib_function('get_wind_speed')(np.asfortranarray(pos_g, dtype=np.float64),
                                                       np.asfortranarray([0, 0, 0], dtype=np.float64))[0][1]

    def get_uvw(self, pos_g):
        vx, vy, vz = self.get_wind_speed(pos_g)
        return [vy, vx, -vz]

    def get_time(self):
        return np.round(H2LibSignatures.get_time(self, time=0.)[0][0], 6)

    def read_input(self, htc_path, model_path='.'):
        if htc_path is not None:
            self._model_path = model_path
            self.cwd = self.model_path
            return H2LibSignatures.read_input(self, htc_path)

    def init(self, htc_path=None, model_path='.'):
        assert not self._initialized, "h2lib already initialized via init, init_AD or init_AL"
        self.read_input(htc_path, model_path)
        r = H2LibSignatures.init(self)
        self._initialized = True
        return r

    def init_AD(self, htc_path=None, model_path='.', tiploss_method=2, tiploss2_shen_c2=21, tiploss2_shen_h=0, rotor=0):
        """Initialize HAWC2 for Actuator Disc workflow, where wind speeds including induction at the aerodynamic sections
        are passed from e.g. CFD to HAWC2 via set_aerosections_windspeed.
        This function will:
        - Disable wind speed update at blade sections (wind speeds must be set via set_aerosections_windspeed)
        - Disable HAWC2 induction (induction_method=0).
        - set GetWindSpeedData%u_mean=nan to avoid unintended use of the free wind module in HAWC2
        - set the tiploss_method. The default method is 2, which works with the AD workflow,
          but the tiploss2_shen_c2 and tiploss2_shen_h parameters must be tuned to give sensible results,
          see tiploss_method in the HAWC2 manual
        """
        assert not self._initialized, "h2lib already initialized via init, init_AD or init_AL"
        self.read_input(htc_path, model_path)
        r = H2LibSignatures.init_AD(self, rotor + 1, int(tiploss_method),
                                    float(tiploss2_shen_c2), float(tiploss2_shen_h))
        self._initialized = True
        return r

    def init_AL(self, epsilon_smearing, htc_path=None, model_path='.', rotor=0):
        """Initialize HAWC2 for Actuator Line workflow, where wind speeds including induction at the aerodynamic sections
        are passed from e.g. CFD to HAWC2 via set_aerosections_windspeed.
        This function will:
        - Disable wind speed update at blade sections (wind speeds must be set via set_aerosections_windspeed)
        - Enable viscous core correction which compensates for the missing induction due to smearing of the forces.
          The method calculates the missing induction as a smearing factor times the normal near wake induction
          (induction_method=2) while disregarding the BEM farwake contribution.
          The smearing factor is based on the smearing size given by epsilon_smearing [m].
        - set GetWindSpeedData%u_mean=nan to avoid unintended use of the free wind module in HAWC2
        - set the tiploss_method to 0, to avoid unintended additional tiploss correction
        """
        assert not self._initialized, "h2lib already initialized via init, init_AD or init_AL"
        self.read_input(htc_path, model_path)
        r = H2LibSignatures.init_AL(self, rotor=rotor + 1, epsilon_smearing=float(epsilon_smearing))
        self._initialized = True
        return r

    def step(self):
        self.time = np.round(H2LibSignatures.step(self, restype=np.float64)[1], 6)
        return self.time

    def predict(self):  # pragma: no cover
        """Temporary functions to reproduce results from old cpl coupling"""
        self.get_lib_function('step_predict_hawc2')()

    def correct(self):  # pragma: no cover
        """Temporary functions to reproduce results from old cpl coupling"""
        self.get_lib_function('step_correct_hawc2')()

    def run(self, time):
        self.time = np.round(H2LibSignatures.run(self, np.float64(time), restype=np.float64)[1], 6)
        return self.time

    def check_convergence(self):
        """
        Check the convergence of the simulation. Typically, after a time step or a call to the static solver.

        Returns
        -------
        bconv : bool
            `True` if the solution has converged.
        resq : real
            Residual on internal-external forces.
        resg : real
            Residual on constraint equations.
        resd : real
            Residual on increment.
        """
        bconv = False
        resq = -1.0
        resg = -1.0
        resd = -1.0
        bconv, resq, resg, resd = H2LibSignatures.check_convergence(self, bconv, resq, resg, resd)[0]
        return bconv, resq, resg, resd

    def linearize(self):
        """
        Linearize the system, as done by the system eigen-analysis.

        Returns
        -------
        n_tdofs : int
            Total number of degrees of freedom in the system.
        n_rdofs : int
            Number of degrees of freedom in the reduced order system.

        """
        n_tdofs = -1
        n_rdofs = -1
        res = H2LibSignatures.linearize(self, n_tdofs, n_rdofs)[0]
        return res

    def do_system_eigenanalysis(self, n_modes, include_damping=True):
        """
        Do the system eigen-analysis.

        Parameters
        ----------
        n_modes : int
            Number of modes to output.
        include_damping : bool, optional
            `True` to include damping, `False` otherwise. The default is `True`.

        Raises
        ------
        RuntimeError
            Call `linearize` first.
        ValueError
            If too many modes are requested.

        Returns
        -------
        natural_frequencies : (n_modes,) ndarray
            Natural frequencies, in Hz.
        damping_ratios : (n_modes,) ndarray
            Damping ratios (nondimensional).
            Only returned if `include_damping=True`.

        """
        natural_frequencies = np.zeros((n_modes,), dtype=np.float64, order="F")
        damping_ratios = np.zeros((n_modes,), dtype=np.float64, order="F")
        error_code = -1

        _, _, natural_frequencies, damping_ratios, error_code = (
            H2LibSignatures.do_system_eigenanalysis(
                self,
                include_damping,
                n_modes,
                natural_frequencies,
                damping_ratios,
                error_code,
            )[0]
        )

        if error_code > 0:
            raise _ERROR_CODES[error_code]

        if include_damping:
            return natural_frequencies, damping_ratios
        else:
            return natural_frequencies

    def get_system_eigenvalues_and_eigenvectors(
        self, n_modes, n_rdofs, include_damping=True
    ):
        """
        Get the system eigenvalues and eigenvectors from system_eigenanalysis.

        This function must be called after `do_system_eigenanalysis`, with the same value of `include_damping`.

        Parameters
        ----------
        n_modes : int
            Number of modes to output.
        n_rdofs : int
            Number of degrees of freedom in the reduced order system.
            As returned by `linearize`.
        include_damping : bool, optional
            `True` to include damping, `False` otherwise. The default is `True`.

        Raises
        ------
        RuntimeError
            If the structure is confidential or if `linearize` and `do_system_eigenanalysis` have not been called first.
        ValueError
            Either `n_modes` or `n_rdofs` is wrong.

        Returns
        -------
        eigenvalues : (n_modes,) ndarray
            Eigenvalues. Real array without damping and complex array otherwise.
        eigenvectors : (n_modes, ny)
            Eigenvectors. Real array without damping and complex array otherwise.
            Only returned if the structure is not confidential.

        """
        if include_damping:
            ny = 2 * n_rdofs
            dtype = np.complex128
            f = H2LibSignatures.get_system_eigval_eigvec_with_damping
        else:
            ny = n_rdofs
            dtype = np.float64
            f = H2LibSignatures.get_system_eigval_eigvec_without_damping

        error_code = -1
        eigenvalues = np.zeros((n_modes,), dtype=dtype, order="F")
        eigenvectors = np.zeros((n_modes, ny), dtype=dtype, order="F")

        _, _, eigenvalues, eigenvectors, error_code = f(
            self, n_modes, ny, eigenvalues, eigenvectors, error_code
        )[0]

        if error_code > 0:
            if error_code == 4:
                # The structure is confidential.
                # The eigenvectors have not been returned by the Fortran code.
                return eigenvalues
            else:
                raise _ERROR_CODES[error_code]

        return eigenvalues, eigenvectors

    def solver_static_init(self):
        """
        Initialize the static solver.

        Returns
        -------
        None.

        """
        H2LibSignatures.solver_static_init(self)

    def solver_static_update(self):
        """
        Update the static solver.

        Raises
        ------
        RuntimeError
            If the static solver has not been initialized. Call `solver_static_init()` first.

        Returns
        -------
        None.

        """
        error_code = -1
        error_code = H2LibSignatures.solver_static_update(self, error_code)[0][0]
        if error_code > 0:
            raise _ERROR_CODES[error_code]

    def solver_static_solve(self):
        """
        Compute the static solution.

        Raises
        ------
        RuntimeError
            If the static solver has not been initialized. Call `solver_static_init()` first.

        Returns
        -------
        None.

        """
        error_code = -1
        error_code = H2LibSignatures.solver_static_solve(self, error_code)[0][0]
        if error_code > 0:
            raise _ERROR_CODES[error_code]

    def solver_static_delete(self):
        """
        Delete the static solver.

        Returns
        -------
        None.

        """
        H2LibSignatures.solver_static_delete(self)

    def solver_static_run(self, reset_structure=False):
        """
        Run the complete static solver algorithm.

        When the calls to the static solver are independent, it may be convenient to
        set `reset_structure = True`, so that the staic solver will run from the
        undeflected configuration, as specified in the htc file. On the other hand,
        if the static solver is obtained for increasing wind speeds, then it is convenient
        to start from the last converged solution, thus setting `reset_structure = False`,
        as done by HAWCStab2.

        Parameters
        ----------
        reset_structure : bool, optional,
            If `True` this function will reset the structure deflection and orientation
            before running the static solver. The default is `False`.

        Raises
        ------
        RuntimeError
            If the static solver has not converged.

        Returns
        -------
        None.

        """
        error_code = -1
        _, error_code = H2LibSignatures.solver_static_run(self, reset_structure, error_code, check_stop=False)[0]
        if error_code > 0:
            raise _ERROR_CODES[error_code]

    def structure_reset(self):
        """Reset the structure deflection and orientation."""
        H2LibSignatures.structure_reset(self)

    def add_sensor(self, sensor_line):
        """Add sensor to hawc2. The sensor will be accessible from h2lib but will not show up in the output file of HAWC2
        Note, that some sensors consist of multiple HAWC2 sensors, e.g. "wind free_wind" which has a Vx, Vy and Vz sensors

        Parameters
        ----------
        Sensor_line : str
            Sensor line as used in the output sections in HAWC2. See How2Hawc2

        Returns
        -------
        index_lst : list
            List of sensor index(es). These index(es) can be used to call get_sensor_info or get_sensor_values
        """
        if ";" not in sensor_line:
            sensor_line += ";"
        index_start, index_stop = 0, 0
        index_start, index_stop = H2LibSignatures.add_sensor(self, sensor_line.lower(), index_start, index_stop)[0][1:]
        return tuple(range(index_start, index_stop + 1))

    def get_sensor_info(self, id):
        "return name, unit, description"
        if isinstance(id, tuple):
            return [self.get_sensor_info(i) for i in id]
        return [s[:-1].strip()  # remove null termination
                for s in H2LibSignatures.get_sensor_info(self, id, name=" " * 30, unit=" " * 10, desc=" " * 512)[0][1:]]

    def get_sensor_values(self, id_lst):
        """Get sensor values from HAWC2

        Parameters
        ----------
        id_lst : array_like or int
            list of sensor ids

        Returns
        -------
        values : array_like or float
        """
        if isinstance(id_lst, int):
            return self.get_sensor_values([id_lst])[0]
        values = np.zeros(len(id_lst), dtype=np.float64)
        id_lst = np.array(id_lst, dtype=np.int64)
        return H2LibSignatures.get_sensor_values(self, id_lst, values, len(id_lst))[0][1]

    def set_variable_sensor_value(self, id, value):
        return H2LibSignatures.set_variable_sensor_value(self, id, np.float64(value))

    def set_orientation_base(
        self,
        main_body,
        mbdy_eulerang_table=None,
        angles_in_deg=True,
        reset_orientation=False,
        mbdy_ini_rotvec_d1=None,
    ):
        """
        Set an `orientation` / `base` command.

        Function equivalent to the HAWC2 command `orientation` / `base`.
        For further details see the HAWC2 documentation.
        We assume that this base orientation is already present in the htc file,
        and therefore modify it here instead of creating a new one.

        Parameters
        ----------
        main_body : str
            Main body name. Same as HAWC2 `mbdy` parameter.
        mbdy_eulerang_table : (:, 3) ndarray, optional
            A sequence of Euler angles, one per row.
            Equivalent to HAWC2 command `mbdy_eulerang`.
            A 1D array with 3 elements will be interpreted as 1 row.
            This table is additive with respect to the orientation / base command in the htc file,
            unless the flag `reset_orientation` is used.
            The default is `[0, 0, 0]`, which means that no rotation is applied.
        angles_in_deg : bool, optional
            `True` if the angles in `mbdy_eulerang_table` are provided in degrees.
            `False` if they are in radians.
            The default is `True`.
        reset_orientation : bool, optional,
            If `True` this function will reset the orientation to the global frame
            before applying `mbdy_eulerang_table`. The default is `False`.
        mbdy_ini_rotvec_d1 : (4) ndarray, optional
            Angular velocity. First 3 elements for the direction and last for the magnitude.
            Equivalent to HAWC2 command `mbdy_ini_rotvec_d1`.
            The default is 0 speed.

        Raises
        ------
        ValueError
            If the `orientation` / `base` command cannot be found.

        Returns
        -------
        None.

        """
        if mbdy_eulerang_table is None:
            mbdy_eulerang_table = np.zeros((1, 3), dtype=np.float64, order="F")
        if mbdy_ini_rotvec_d1 is None:
            mbdy_ini_rotvec_d1 = np.zeros((4,), dtype=np.float64, order="F")
        # 1D arrays are converted to 2D with 1 row.
        mbdy_eulerang_table = np.atleast_2d(mbdy_eulerang_table)
        error_code = -1
        error_code = H2LibSignatures.set_orientation_base(
            self,
            main_body,
            mbdy_eulerang_table.shape[0],
            np.asfortranarray(mbdy_eulerang_table.astype(np.float64)),
            bool(angles_in_deg),
            bool(reset_orientation),
            np.asfortranarray(mbdy_ini_rotvec_d1.astype(np.float64)),
            error_code,
        )[0][-1]

        if error_code > 0:
            raise _ERROR_CODES[error_code]

    def set_orientation_relative(
        self,
        main_body_1,
        node_1,
        main_body_2,
        node_2,
        mbdy2_eulerang_table=None,
        angles_in_deg=True,
        reset_orientation=False,
        mbdy2_ini_rotvec_d1=None,
    ):
        """
        Set an `orientation` / `relative` command.

        Function equivalent to the HAWC2 command `orientation` / `relative`.
        For further details see the HAWC2 documentation.
        We assume that this relative orientation is already present in the htc file,
        and therefore modify it here instead of creating a new one.

        Parameters
        ----------
        main_body_1 : str
            Main body name to which the next main body is attached.
        node_1 : int, str
            Node number of `main_body_1` that is used for connection, starting from 0.
            `"last"` can be specified which ensures that the last node on the main_body
            is used, and `-1` refers to the origin of the main body coordinate system.
        main_body_2 : str
            Main_body name of the `main_body` that is positioned
            in space by the relative command.
        node_2 : int, str
            Node number of `main_body_2` that is used for connection, starting from 0.
            `"last"` can be specified which ensures that the last node on the main_body
            is used, and `-1` refers to the origin of the main body coordinate system.
        mbdy2_eulerang_table : : (:, 3) ndarray, optional
            A sequence of Euler angles, one per row.
            Equivalent to HAWC2 command `mbdy2_eulerang`.
            A 1D array with 3 elements will be interpreted as 1 row.
            This table is additive with respect to the orientation / relative command in the htc file,
            unless the flag `reset_orientation` is used.
            The default is `[0, 0, 0]`, which means that no rotation is applied.
        angles_in_deg : bool, optional
            `True` if the angles in `mbdy2_eulerang_table` are provided in degrees.
            `False` if they are in radians.
            The default is `True`.
        reset_orientation : bool, optional,
            If `True` this function will reset the orientation to no rotation
            before applying `mbdy2_eulerang_table`. The default is `False`.
        mbdy2_ini_rotvec_d1 : (4) ndarray or list, optional
            Angular velocity. First 3 elements for the direction and last for the magnitude.
            Equivalent to HAWC2 command `mbdy2_ini_rotvec_d1`.
            The default is 0 speed.

        Raises
        ------
        ValueError
            If the `orientation` / `relative` command cannot be found,
            or if the main bodies do not exist.

        Returns
        -------
        None.

        """
        if mbdy2_eulerang_table is None:
            mbdy2_eulerang_table = np.zeros((1, 3), dtype=np.float64, order="F")
        if mbdy2_ini_rotvec_d1 is None:
            mbdy2_ini_rotvec_d1 = np.zeros((4,), dtype=np.float64, order="F")
        # 1D arrays are converted to 2D with 1 row.
        mbdy2_eulerang_table = np.atleast_2d(mbdy2_eulerang_table)
        # Convert node_1 and 2 to int.
        if node_1 == "last":
            node_1 = -2
        if node_2 == "last":
            node_2 = -2
        error_code = -1
        error_code = H2LibSignatures.set_orientation_relative(
            self,
            main_body_1,
            node_1 + 1,
            main_body_2,
            node_2 + 1,
            mbdy2_eulerang_table.shape[0],
            np.asfortranarray(mbdy2_eulerang_table.astype(np.float64)),
            bool(angles_in_deg),
            reset_orientation,
            np.asfortranarray(mbdy2_ini_rotvec_d1).astype(np.float64),
            error_code,
            check_stop=False)[0][-1]
        if error_code > 0:
            raise _ERROR_CODES[error_code]

    def init_windfield(self, Nxyz, dxyz, box_offset_yz, transport_speed):
        """Initialize wind field which afterwards can be set using set_windfield


        x: direction of wind
        y: horizontal to the left when looking along x
        z: vertical up

        Parameters
        ----------
        Nxyz : (int, int, int)
            Number of points in wind field
        dxyz : (float, float, float)
            Distance between wind field points
        box_offset_yz : (float, float)
            Box offset in y and z, relative to hawc2 origo. Note this is in met coordinates as described above
            To set a wind field of size 200x80x80, such that the center is located at hawc2 coordinate (0,0,-70),
            box_offset_yz must be (-40,30)
            Note that the wind field size is (Nxyz)-1*dxyz
        transport_speed : float
            Box transport speed

        Notes
        -----
        The wind field will be transported in the hawc2 global y-direction with the transport speed,
        In HAWC2:
        - shear format is set to 0 (which also means that the mean wind (transport speed) is not added)
        - turbformat is set to 1 (mann), but the buffer should be filled manually via set_windfield
        - center_pos0 is set such that the lower right corner (when looking along global y) is located at box_offset_yz
        - windfield_rotations is set to (0,0,0), i.e. the wind is aligned with y, and w points up (opposite global z)
        - scaling is disabled
        - the buffer is interpolated in the standard way, i.e. it is mirrored in the lateral and vertical direction and
          repeated in the longitudinal direction

        """
        return H2LibSignatures.init_windfield(self, np.array(Nxyz, dtype=np.int64), np.array(dxyz, dtype=np.float64),
                                              np.array(box_offset_yz, dtype=np.float64), np.float64(transport_speed))

    def set_windfield(self, uvw, box_offset_x, time=None):
        """Set wind field, must be called after init_windfield and init

        Parameters
        ----------
        uvw : array_like, dims=(3,Nx,Ny,Nz)
            wind field components including mean wind speed, shear etc.
        box_offset_x : float
            Offset in x direction at the <time>
            To set a wind field of size 200x80x80, such that the front plane (largest x) is located
            at hawc2 coordinate (0,20,-70), i.e. 20m downstream of origo, set box_offset_x=-180
            Note that the wind field size is (Nxyz)-1*dxyz
            Note also that the end plane (x=0) will be located in -180 and repeated in 20+dx
        time : float, optional
            Time at which the the last plane (x=0) is at x=box_offset_x
            If None, default, time is set to the current time in HAWC2

        Notes
        -----
        uvw must be scaled in advance to the right turbulence level
        and should contain mean wind, shear, gusts, direction change etc.
        and uvw(:,1) is the back plane of the turbulence box, while uvw(:,Nx) is the front plane
        """
        if time is None:
            time = self.get_time()
        uvw = np.asfortranarray(uvw, dtype=np.float32)
        assert np.all(np.isfinite(uvw)), "uvw passed to h2lib.set_windfield contains nan or inf"
        return H2LibSignatures.set_windfield(self, uvw, np.float64(box_offset_x), np.float64(time))

    def set_c2_def(
        self, main_body_name, c2_def, twist_in_deg=True, check_length=True
    ):
        """
        Set c2_def, which defines the centerline of the specified main body.

        Parameters
        ----------
        main_body_name : str
            Name of main body that must be updated.
        c2_def : (:, 4) ndarray
            New c2_def. It is an array with at least 2 rows and 4 columns for x, y, z and twist.
            The number of rows, i.e. sections, must match the ones in the original c2_def.
        twist_in_deg : bool, optional
            `True` if the twist (last column in c2_def) is given in [deg].
            `False` if it is given in [rad]. The default is `True`.
        check_length : bool, optional
            `True` if the new beam length needs to be checked, `False` otherwise. The default is `False`.

        Raises
        ------
        ValueError
            Can be due to:
                - MAIN_BODY_NOT_FOUND: none of the main bodies is called `main_body_name`.
                - TOO_FEW_SECTIONS_IN_C2DEF: `c2_def` must have at least 2 sections, i.e. rows.
                - BEAM_TOO_SHORT: the minimum beam length is 1.0e-7.
                - DIFFERENT_NSEC: this command does not allow to add or remove sections,
                                  therefore `c2_def` must have the same number of sections as in the HAWC2 model.
        NotImplementedError
            Only the c2_def node distribution is supported.

        Returns
        -------
        None.

        """
        error_code = -1
        error_code = H2LibSignatures.set_c2_def(
            self,
            main_body_name,
            np.asfortranarray(c2_def.astype(np.float64)),
            c2_def.shape[0],
            bool(twist_in_deg),
            bool(check_length),
            error_code,
            check_stop=False,
        )[0][-1]

        if error_code > 0:
            raise _ERROR_CODES[error_code]

    # ===================================================================================================================
    # H2rotor
    # ===================================================================================================================

    def get_rotor_dims(self):
        return [[self.get_nSections(r, b) for b in range(self.get_nblades(r))]
                for r in range(self.get_nrotors())]

    def get_nrotors(self):
        return H2LibSignatures.get_nrotors(self, restype=np.int64)[1]

    def get_nblades(self, rotor=0):
        return H2LibSignatures.get_nblades(self, rotor + 1, restype=np.int64)[1]

    def get_nSections(self, rotor=0, blade=0):
        return H2LibSignatures.get_nSections(self, rotor + 1, blade + 1, restype=np.int64)[1]

    def get_diameter(self, rotor=0):
        return H2LibSignatures.get_diameter(self, rotor + 1, restype=np.float64)[1]

    def aero_sections_data_shape(self, rotor):
        if rotor not in self._aero_sections_data_shape:
            self._aero_sections_data_shape[rotor] = (self.get_nblades(rotor), self.get_nSections(rotor), 3)
        return self._aero_sections_data_shape[rotor]

    def get_aerosections_position(self, rotor=0):
        """Global xyz position of aero sections. Shape=(#blades, #sections, 3)"""
        position = np.zeros(self.aero_sections_data_shape(rotor), dtype=np.float64, order='F')
        return H2LibSignatures.get_aerosections_position(self, rotor + 1, position)[0][1]

    def set_aerosections_windspeed(self, uvw, rotor=0):
        """Update wind speed at aero sections. uvw shape=(#blades, #sections, 3)"""
        return H2LibSignatures.set_aerosections_windspeed(self, rotor + 1, np.asfortranarray(uvw, np.float64))

    def get_aerosections_forces(self, rotor=0):
        shape = self.aero_sections_data_shape(rotor)
        Fxyz = np.zeros(shape, dtype=np.float64, order='F')
        return H2LibSignatures.get_aerosections_forces(self, rotor + 1, Fxyz)[0][1]

    def get_aerosections_moments(self, rotor=0):
        shape = self.aero_sections_data_shape(rotor)
        Mxyz = np.zeros(shape, dtype=np.float64, order='F')
        return H2LibSignatures.get_aerosections_moments(self, rotor + 1, Mxyz)[0][1]

    def get_bem_grid_dim(self, rotor=0):
        """returns (nazi, nrad)"""
        return H2LibSignatures.get_bem_grid_dim(self, rotor + 1, 0, 0)[0][1:]

    def get_bem_grid(self, rotor=0):
        """returns azi, rad"""
        nazi, nrad = self.get_bem_grid_dim(rotor)
        return H2LibSignatures.get_bem_grid(self, rotor + 1,
                                            np.zeros(nazi, dtype=np.float64, order='F'),
                                            np.zeros(nrad, dtype=np.float64, order='F'))[0][1:]

    def get_induction_polargrid(self, rotor=0):
        nazi, nrad = self.get_bem_grid_dim(rotor)
        induction = np.zeros((nazi, nrad), dtype=np.float64, order='F')
        return H2LibSignatures.get_induction_polargrid(self, rotor + 1, induction)[0][1]

    def get_induction_axisymmetric(self, rotor=0):
        nrad = self.get_bem_grid_dim(rotor)[1]
        induction = np.zeros(nrad, dtype=np.float64)
        return H2LibSignatures.get_induction_axisymmetric(self, rotor + 1, induction)[0][1]

    def get_induction_rotoravg(self, rotor=0):
        induction = np.float64(0)
        return H2LibSignatures.get_induction_rotoravg(self, rotor + 1, induction)[0][1]

    def get_rotor_orientation(self, rotor=0, deg=False):
        """return yaw, tilt, azi(of first blade) in rad(default) or deg"""
        r = H2LibSignatures.get_rotor_orientation(self, rotor=rotor + 1, yaw=0., tilt=0., azi=0.)[0][1:]
        if deg:
            return np.rad2deg(r)
        else:
            return r

    def get_rotor_position(self, rotor=0):
        return H2LibSignatures.get_rotor_position(self, rotor=rotor + 1, position=np.zeros(3, dtype=np.float64))[0][1]

    def get_rotor_avg_wsp(self, coo=1, rotor=0):
        """Returns the rotor averaged wind speed in global(coo=1, default) or rotor(coo=2) coordinates."""
        assert self.time > 0
        wsp = np.zeros(3, dtype=np.float64)
        return H2LibSignatures.get_rotor_avg_wsp(self, coo=coo, rotor=rotor + 1, wsp=wsp)[0][2]

    def get_rotor_avg_uvw(self, rotor=0):
        vx, vy, vz = self.get_rotor_avg_wsp(1, rotor)
        return [vy, vx, -vz]

    def get_number_of_bodies_and_constraints(self):
        """
        Get number of bodies and constraints.

        Raises
        ------
        RuntimeError
            If the structure is confidential.

        Returns
        -------
        nbdy : int
            Number of bodies.
        ncst : int
            Number of constraints.

        """
        nbdy = -1
        ncst = -1
        error_code = -1
        (
            nbdy,
            ncst,
            error_code,
        ) = H2LibSignatures.get_number_of_bodies_and_constraints(
            self, nbdy, ncst, error_code, check_stop=False
        )[
            0
        ]
        if error_code > 0:
            raise _ERROR_CODES[error_code]
        return nbdy, ncst

    def get_number_of_elements(self):
        """
        Get the number of elements for each body.

        Raises
        ------
        RuntimeError
            If the structure is confidential.

        Returns
        -------
        nelem : (nbdy) ndarray, int
            Number of elements for each body.

        """
        nbdy, _ = self.get_number_of_bodies_and_constraints()

        nelem = np.zeros((nbdy, ), dtype=np.int64, order="F")
        error_code = -1
        _, nelem, error_code = H2LibSignatures.get_number_of_elements(
            self, nbdy, nelem, error_code, check_stop=False
        )[0]

        if error_code > 0:  # pragma: no cover
            # This cannot happen because exceptions are raised by get_number_of_bodies_and_constraints().
            raise _ERROR_CODES[error_code]  # pragma: no cover
        return nelem

    def get_timoshenko_location(self, ibdy, ielem):
        """
        Get the location and orientation of an element.

        Parameters
        ----------
        ibdy : int
            Body index, starting from 0.
        ielem : int
            Element index, starting from 0.

        Raises
        ------
        RuntimeError
            If the structure is confidential.
        IndexError
            If the body or the element do not exist.

        Returns
        -------
        l : float
            Element length.
        r1 : (3) ndarray
            Location of node 1.
        r12 : (3) ndarray
            Vector from node 1 to node 2.
        tes : (3, 3) ndarray
            Transformation matrix describing orientation.

        """

        l = 0.0
        r1 = np.zeros((3), order="F")
        r12 = np.zeros((3), order="F")
        tes = np.zeros((3, 3), order="F")
        error_code = -1
        (
            _,
            _,
            l,
            r1,
            r12,
            tes,
            error_code,
        ) = H2LibSignatures.get_timoshenko_location(
            self, ibdy + 1, ielem + 1, l, r1, r12, tes, error_code, check_stop=False)[0]
        if error_code > 0:
            raise _ERROR_CODES[error_code]
        return l, r1, r12, tes

    def get_body_rotation_tensor(self, ibdy):
        """
        Get the rotation tensor of the requested body, that transforms from local to global base.

        Parameters
        ----------
        ibdy : int
            Body index, starting from 0.

        Raises
        ------
        RuntimeError
            If the structure is confidential.
        IndexError
            If the body does not exist.

        Returns
        -------
        amat : (3, 3) ndarray
            Rotation tensor.

        """
        amat = np.zeros((3, 3), order="F")
        error_code = -1
        _, amat, error_code = H2LibSignatures.get_body_rotation_tensor(
            self, ibdy + 1, amat, error_code, check_stop=False)[0]
        if error_code > 0:
            raise _ERROR_CODES[error_code]
        return amat

    def body_output_mass(self, ibdy):
        """
        Compute body mass properties. Wrapper of HAWC2 command `new_htc_structure / body_output_file_name`.

        Parameters
        ----------
        ibdy : int
            Body index, starting from 0.

        Raises
        ------
        RuntimeError
            If the structure is confidential.
        IndexError
            If the body does not exist.

        Returns
        -------
        body_mass : float
            Body mass [kg].
        body_inertia : (6,) ndarray
            Body inertia [Ixx, Iyy, Izz, Ixy, Ixz, Iyz] in [kg*m^2].
        cog_global_frame : (3,) ndarray
            Body center of gravity in the global frame [m].
        cog_body_frame : (3,) ndarray
            Body center of gravity in the body frame [m].
        """
        body_mass = 0.0
        body_inertia = np.zeros((6,), order="F")
        cog_global_frame = np.zeros((3,), order="F")
        cog_body_frame = np.zeros((3,), order="F")
        error_code = -1

        _, body_mass, body_inertia, cog_global_frame, cog_body_frame, error_code = (
            H2LibSignatures.body_output_mass(
                self,
                ibdy + 1,
                body_mass,
                body_inertia,
                cog_global_frame,
                cog_body_frame,
                error_code,
                check_stop=False,
            )[0]
        )
        if error_code > 0:
            raise _ERROR_CODES[error_code]
        return body_mass, body_inertia, cog_global_frame, cog_body_frame

    def body_output_element(self, ibdy, ielem):
        """
        Compute element matrices. Wrapper of HAWC2 command `new_htc_structure / element_matrix_output`.

        Parameters
        ----------
        ibdy : int
            Body index, starting from 0.
        ielem : int
            Element index, starting from 0.

        Raises
        ------
        RuntimeError
            If the structure is confidential.
        IndexError
            If the body or the element do not exist.

        Returns
        -------
        mass : (12, 12) ndarray of float
            Mass matrix.
        stiffness : (12, 12) ndarray of float
            Mass matrix.
        damping : (12, 12) ndarray of float
            Mass matrix.
        """
        mass = np.zeros((12, 12), dtype=np.float64, order="F")
        stiffness = np.zeros_like(mass)
        damping = np.zeros_like(mass)
        error_code = -1
        _, _, mass, stiffness, damping, error_code = H2LibSignatures.body_output_element(
            self,
            ibdy + 1,
            ielem + 1,
            mass,
            stiffness,
            damping,
            error_code,
            check_stop=False,
        )[0]
        if error_code > 0:
            raise _ERROR_CODES[error_code]
        return mass, stiffness, damping

    def get_system_matrices(self, n_tdofs, n_rdofs):
        """
        Get the system structural matrices computed during the system_eigenanalysis.

        This function must be called after `linearize()`.

        Parameters
        ----------
        n_tdofs : int
            Total number of degrees of freedom in the system.
        n_rdofs : int
            Number of degrees of freedom in the reduced order system.

        Raises
        ------
        RuntimeError
            If the linearizetion has not been done or the structure is confidential.
        ValueError
            If the total or reduced number of degrees of freedom is wrong.

        Returns
        -------
        M : (n_rdofs, n_rdofs) ndarray
            Mass matrix.
        C : (n_rdofs, n_rdofs) ndarray
            Damping matrix.
        K : (n_rdofs, n_rdofs) ndarray
            Stiffness matrix.
        R : (n_tdofs, n_rdofs) ndarray
            Transformation between reduced and all DOFs.

        """
        M = np.zeros((n_rdofs, n_rdofs), dtype=np.float64, order="F")
        C = np.zeros((n_rdofs, n_rdofs), dtype=np.float64, order="F")
        K = np.zeros((n_rdofs, n_rdofs), dtype=np.float64, order="F")
        R = np.zeros((n_tdofs, n_rdofs), dtype=np.float64, order="F")
        error_code = -1

        _, _, M, C, K, R, error_code = H2LibSignatures.get_system_matrices(
            self, n_tdofs, n_rdofs, M, C, K, R, error_code, check_stop=False)[0]

        if error_code > 0:
            raise _ERROR_CODES[error_code]
        return M, C, K, R

    def get_no_mainbodies(self):
        return H2LibSignatures.get_number_of_mainbodies(self, restype=np.int64)[1]

    def get_mainbody_name_dict(self):
        s = " " * 256
        return {H2LibSignatures.get_mainbody_name(self, mainbody_nr=int(i), mainbody_name=s)[0][1].strip(): i
                for i in np.arange(self.get_no_mainbodies()) + 1}

    def get_mainbody_position_orientation(self, mainbody_nr, mainbody_coo_nr=0):
        mbdy_pos = np.zeros(3, dtype=np.float64, order="F")
        mbdy_tbg = np.zeros((3, 3), dtype=np.float64, order="F")
        return H2Lib_DistributedSections.get_mainbody_position_orientation(
            self, int(mainbody_nr), mbdy_pos, mbdy_tbg, int(mainbody_coo_nr))[0][1:-1]


@contextmanager
def set_LD_LIBRARY_PATH():
    old = os.environ.get('LD_LIBRARY_PATH', "")
    import site
    lsts = [site.getsitepackages(), site.getusersitepackages()]
    libs = [p[:p.index('/lib/') + 5] for lst in lsts for p in (lst, [lst])[isinstance(lst, str)] if '/lib/' in p]
    lib64s = [p[:p.index('/lib64/') + 7] for lst in lsts for p in (lst, [lst])[isinstance(lst, str)] if '/lib64/' in p]
    lib_paths = ":".join(libs + lib64s)
    os.environ['LD_LIBRARY_PATH'] = f'{lib_paths}:{old}'

    try:
        yield
    finally:
        os.environ['LD_LIBRARY_PATH'] = old


class H2LibProcess(ProcessClass, H2LibThread):
    def __init__(self, suppress_output, filename=None, cwd='.'):
        with set_LD_LIBRARY_PATH():
            ProcessClass.__init__(self, cls=H2LibThread, cls_attrs=set(dir(H2LibThread)) - set(dir(ProcessClass)))
            self(suppress_output=suppress_output, filename=filename, cwd=cwd)


def H2Lib(suppress_output=False, subprocess=True, cwd='.', filename=None) -> H2LibThread:
    H2 = [H2LibThread, H2LibProcess][subprocess]
    return H2(suppress_output=suppress_output, cwd=cwd, filename=filename)


def MultiH2Lib(N, filename=None, cwd='.', suppress_output=False):

    if not hasattr(suppress_output, '__len__'):
        suppress_output = [suppress_output] * N
    args = [(suppress_output[i], filename, cwd) for i in range(N)]

    with set_LD_LIBRARY_PATH():
        from multiclass_interface import mpi_interface
        if mpi_interface.mpi:  # pragma: no cover
            # try:
            #     with H2LibThread(filename):
            #         pass
            #     # LD_LIBRARY_PATH is set. Run H2LibThread directly in mpi processes
            #     cls = H2LibThread
            # except OSError:
            #     # Set LD_LIBRARY_PATH in mpi workers and run H2LibThread from the workers via ProcessClass
            #     cls = H2LibProcess
            from multiclass_interface.mpi_interface import MPIClassInterface
            cls = H2LibProcess
            return MPIClassInterface(cls, args)
        else:
            return MultiProcessClassInterface(H2LibThread, args)
