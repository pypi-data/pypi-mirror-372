from not1mm.lib.rot_interface import RotatorInterface

rotator = RotatorInterface()
if rotator.connected is True:
    print(f"{rotator.get_position()=}")
