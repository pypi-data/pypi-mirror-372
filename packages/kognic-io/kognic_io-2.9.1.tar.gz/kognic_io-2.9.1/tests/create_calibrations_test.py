from __future__ import absolute_import

from datetime import datetime

import pytest

import examples.calibration.create_calibrations as create_calibrations_example
import examples.calibration.get_calibrations as get_calibrations_example
import kognic.io.client as IOC
from kognic.io.model.calibration.calib import SensorCalibrationEntry


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestCalibration:
    calibration_identifier = f"<calibration-{datetime.now()}"

    def test_create_calibration(self, client: IOC.KognicIOClient):
        calibrations = create_calibrations_example.run(client, self.calibration_identifier)
        assert calibrations.external_id == self.calibration_identifier

    def test_get_calibrations(self, client: IOC.KognicIOClient):
        calibrations = get_calibrations_example.run(client)
        assert isinstance(calibrations, list)
        assert all(
            [isinstance(calib, SensorCalibrationEntry) for calib in calibrations]
        ), "Calibrations are not of type SensorCalibrationEntry"

    def test_get_calibration(self, client: IOC.KognicIOClient):
        calibration = client.calibration.get_calibrations(external_id=self.calibration_identifier)
        assert len(calibration) == 1
        assert all(
            [isinstance(calib, SensorCalibrationEntry) for calib in calibration]
        ), "Calibrations are not of type SensorCalibrationEntry"
