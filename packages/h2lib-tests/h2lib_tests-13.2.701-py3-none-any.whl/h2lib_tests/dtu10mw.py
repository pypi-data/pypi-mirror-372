from wetb.hawc2.htc_file import HTCFile
from h2lib_tests.test_files import tfp


class DTU10MW(HTCFile):
    def __init__(self, init_rotor_speed=.2, nbodies=10):
        super().__init__(tfp + "DTU_10_MW/htc/DTU_10MW_RWT.htc")
        o = self.new_htc_structure.orientation.get_subsection_by_name('towertop', 'body1')
        o.mbdy2_ini_rotvec_d1 = 0, 0, -1, init_rotor_speed

        blade = self.new_htc_structure.get_subsection_by_name('blade1')
        blade.nbodies = nbodies

    def set_tilt_cone_yaw(self, tilt, cone, yaw=0):
        r = self.new_htc_structure.orientation.get_subsection_by_name('towertop', 'body1')
        r.body2_eulerang__2 = [tilt, 0, 0]
        r.body2_eulerang__2.comments = "%d deg tilt angle" % tilt
        for i in [1, 2, 3]:
            r = self.new_htc_structure.orientation.get_subsection_by_name('hub%d' % i, 'body2')
            r.body2_eulerang__3 = [cone, 0, 0]
            r.body2_eulerang__3.comments = "%d deg cone angle" % cone
        r = self.new_htc_structure.orientation.get_subsection_by_name('tower', 'body1')
        r.body2_eulerang = [0, 0, yaw]

    def set_straight(self):
        blade = self.new_htc_structure.get_subsection_by_name('blade1')
        blade.timoschenko_input.set = 1, 3
        for i in range(1, 28):
            sec = getattr(blade.c2_def, 'sec__%d' % i)
            i, x, y, z, t = sec.values
            sec.values = [i, 0, 0, z, 0]

    def set_aero(self, aero_calc=1, induction=1, tiploss=1, dynstall=2):
        self.aero.aerocalc_method = aero_calc
        self.aero.induction_method = induction
        self.aero.tiploss_method = tiploss
        self.aero.dynstall_method = dynstall

    def set_fixed_pitch(self, pitch):
        pitch_servo = self.dll.get_subsection_by_name('servo_with_limits')
        pitch_servo.init.constant__6[1] = pitch
        pitch_servo.init.constant__7[1] = pitch

    def set_stiff(self, bodies=['tower', 'shaft', 'blade1']):
        for b in bodies:
            self.new_htc_structure.get_subsection_by_name(b).timoschenko_input.set = 1, 2

    def set_gravity(self, gravity):
        for mb in [s for s in self.new_htc_structure if s.name_ == 'main_body']:
            mb.gravity = gravity

    def set_wind(self, wsp, tint, turb_format, shear=(1, 0)):
        self.wind.wsp = wsp
        self.wind.tint = tint
        self.wind.turb_format = turb_format
        self.wind.shear_format = shear


class DTU10MWSimple(DTU10MW):
    def __init__(self, rotor_speed, pitch, nbodies=10):
        super().__init__(rotor_speed, nbodies=nbodies)
        self.dll.delete()

        for s in [s for s in self.output.sensors if s.type == 'constraint']:
            s.delete()
        shaft_rot = self.new_htc_structure.constraint.get_subsection_by_name('shaft_rot')
        shaft_rot.name_ = 'bearing3'
        shaft_rot.omegas = rotor_speed
        for i in [1, 2, 3]:
            r = self.new_htc_structure.orientation.get_subsection_by_name('hub%d' % i, 'body1')
            r.body2_eulerang = [0, 0, -pitch]
            c = self.new_htc_structure.constraint.get_subsection_by_name('pitch%d' % i)
            c.name_ = 'fix1'
            c.name.delete()
            c.bearing_vector.delete()


class DTU10MWRotor(HTCFile):
    def __init__(self, rotor_speed, pitch, tilt=5, cone=2.5, blade_bodies=10, straight=False):
        super().__init__(tfp + "DTU10MW/htc/DTU_10MW_RWT_Rotor.htc")
        blade = self.new_htc_structure.get_subsection_by_name('blade1')
        blade.nbodies = blade_bodies
        tt_s = self.new_htc_structure.orientation.get_subsection_by_name('shaft', 'body2')
        tt_s.body2_eulerang__2 = tilt, 0, 0

        shaft_rot = self.new_htc_structure.constraint.get_subsection_by_name('shaft_rot')
        shaft_rot.omegas = rotor_speed
        for i in [1, 2, 3]:
            r = self.new_htc_structure.orientation.get_subsection_by_name('blade%d' % i, 'body2')
            r.body2_eulerang__3 = [cone, 0, -pitch]

        if straight:
            blade.timoschenko_input.set = 1, 3
            for i in range(1, 28):
                sec = getattr(blade.c2_def, 'sec__%d' % i)
                i, x, y, z, t = sec.values
                sec.values = [i, 0, 0, z, 0]


if __name__ == '__main__':
    dtu = DTU10MWSimple(1, 2)
    print(dtu)
