from h2lib.h2lib_signatures import H2LibSignatures
import numpy as np
from enum import Enum


class DistributedSections():
    def __init__(self, name, link_type, link_id, nsec):
        self.name = name
        assert isinstance(link_type, LinkType)
        self.link_type = link_type
        self.link_id = link_id
        self.nsec = nsec


class LinkType(Enum):
    BODY = 0  # Distributed sections added via add_distributed_sections
    BLADE = 1  # Aerodyninamic sections of rotor=1.
    AERODRAG = 2  # Aerodrag sections
    HYDRO = 3  # Hydroload sections
    SOIL = 4  # soil sections


class H2Lib_DistributedSections(H2LibSignatures):
    """Distributed sections are sections distributed along a mainbody in HAWC2.
    These sections follows the structure and the position and orientation of the sections can be obtained by
    get_distributed_section_position_orientation.

    Furthermore, forces and moments can be set on the sections via set_distributed_section_force_and_moment

    Distributed sections are used inside HAWC2 for aerodynamic loads, aerodrag, hydro, and soil.
    A reference/link object to these sections can be obtained by get_distributed_sections

    Moreover, custom distributed sections can be added by add_distributed_sections. Remember to call
    initialize_distributed_sections between the last add_distributed_sections and the first usage.
    """

    def add_distributed_sections(self, mainbody_name, section_relative_position):
        """Add custom distributed sections along a mainbody.

        Note, that initialize_distributed_sections (see below) must be called after the last call to
        add_distributed_sections and before first call to get_distributed_sections,
        get_distributed_section_position_orientation and set_distributed_section_force_and_moment
        """
        mbdy_name_dict = self.get_mainbody_name_dict()
        assert mainbody_name in mbdy_name_dict, f"'{mainbody_name}' does not exist. Valid names are {list(mbdy_name_dict.keys())}."
        mbdy_nr = mbdy_name_dict[mainbody_name]
        nsec = len(section_relative_position)
        link_id = H2LibSignatures.add_distributed_sections(
            self,
            mainbody_nr=int(mbdy_nr),
            nsec=nsec,
            sec_rel_pos=np.asfortranarray(section_relative_position, dtype=float),
            link_id=0)[0][-1]
        return DistributedSections(mainbody_name, LinkType.BODY, link_id, nsec)

    def initialize_distributed_sections(self):
        """Initialize distributed sections added by add_distributed_sections.

        Note, that this method must be called after the last call to
        add_distributed_sections and before first call to get_distributed_sections,
        get_distributed_section_position_orientation and set_distributed_section_force_and_moment
        """
        return H2LibSignatures.initialize_distributed_sections(self)

    def get_distributed_sections(self, link_type: LinkType, link_id):
        """Return a DistributedSections link object (needed for get_distributed_section_position_orientation
        and set_distributed_section_force_and_moment).

        To obtain the aerodynamic load sections at blade 3 (only rotor=1 can be accessed):
        h2.get_distributed_sections(LinkType.BLADE, 3)

        Parameters
        ----------
        link_type : LinkType
            Specifies the link type. See enum LinkType
        link_id : integer
            index of link. link_id=1 will reference the first added sections, e.g. blade1
        Returns
        -------
        DistributedSections object
        """
        mbdy_nr, nsec = H2LibSignatures.get_distributed_sections(
            self, link_type.value, link_id, mainbody_nr=0, nsec=0)[0][2:]
        mbdy_name_dict = self.get_mainbody_name_dict()
        mbdy_name = {nr: name for name, nr in mbdy_name_dict.items()}[mbdy_nr]
        return DistributedSections(mbdy_name, link_type, link_id, nsec)

    def get_distributed_section_position_orientation(self, ds: DistributedSections, mainbody_coo_nr=0):
        """
        Parameters
        ----------
        ds : DistributedSections

        Returns
        -------
        sec_pos : array(nsec,3)
        sec_ori : array(nsec,3,3)
            Orientation of section in specified coordinates.
            For mainbody_coo_nr=0, default, the orientation is in global coordinates, i.e. Tsg
        """
        sec_pos = np.zeros((ds.nsec, 3), dtype=np.float64, order="F")
        sec_ori = np.zeros((ds.nsec, 3, 3), dtype=np.float64, order="F")
        return H2LibSignatures.get_distributed_section_position_orientation(
            self, int(ds.link_type.value), int(ds.link_id), int(ds.nsec), sec_pos, sec_ori,
            int(mainbody_coo_nr))[0][3:-1]

    def set_distributed_section_force_and_moment(self, ds: DistributedSections, sec_frc, sec_mom):
        """Set forces and moments at distributed sections

        Parameters
        ----------
        ds : DistributedSections object
            object returned by add_distributed_sections or get_distributed_sections
        sec_frc : array_like
            Section forces pr. length [N/m] in global coordinates, shape=(nsec,3)
        sec_momc : array_like
            Section moments pr. length [Nm/m] in global coordinates, shape=(nsec,3)
        """
        sec_frc = np.asfortranarray(sec_frc, dtype=np.float64)
        sec_mom = np.asfortranarray(sec_mom, dtype=np.float64)
        assert sec_frc.shape == (ds.nsec, 3)
        assert sec_mom.shape == (ds.nsec, 3)

        return H2LibSignatures.set_distributed_section_force_and_moment(
            self, link_type=int(ds.link_type.value), link_id=int(ds.link_id), nsec=int(ds.nsec),
            frc_g=sec_frc, mom_g=sec_mom)

    def set_fsi_loads_h2lib(self, fx, fy, fz, mx, my, mz):  # pragma: no cover
        """Temporary function needed to replicate results of the cpl coupling framework"""
        fx, fy, fz, mx, my, mz = [np.asfortranarray(v, dtype=np.float64) for v in [fx, fy, fz, mx, my, mz]]
        self.get_lib_function('set_fsi_loads_hawc2')(fx, fy, fz, mx, my, mz)
