from compas.geometry import Frame
from compas.tolerance import TOL

from compas_pb import pb_dump_bts
from compas_pb import pb_load_bts

from compas_timber.elements import Beam
from compas_timber.fabrication import JackRafterCut


def test_placeholder():
    beam = Beam(Frame.worldXY(), length=5.0, width=0.2, height=0.3, name="goddamn_beam")

    loaded_beam: Beam = pb_load_bts(pb_dump_bts(beam))

    assert loaded_beam.frame == Frame.worldXY()
    assert TOL.is_close(loaded_beam.length, beam.length)
    assert TOL.is_close(loaded_beam.width, beam.width)
    assert TOL.is_close(loaded_beam.height, beam.height)


def test_processing():
    processing = JackRafterCut("start", 11.2, 33.4, 10.0, 45, 34)

    loaded: JackRafterCut = pb_load_bts(pb_dump_bts(processing))

    assert loaded.PROCESSING_NAME == processing.PROCESSING_NAME
    assert TOL.is_close(processing.start_x, loaded.start_x)
    assert TOL.is_close(processing.start_y, loaded.start_y)
    assert TOL.is_close(processing.angle, loaded.angle)
    assert TOL.is_close(processing.inclination, loaded.inclination)
