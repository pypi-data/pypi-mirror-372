import unittest
import os
import tempfile
from unittest import mock

os.environ["SNOWGLOBE_API_KEY"] = "test"

from src.snowglobe.client.src.config import Config  # noqa: E402

os.environ["SNOWGLOBE_API_KEY"] = ""


class TestConfig(unittest.TestCase):
    def test_get_api_key_env(self):
        with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
            config = Config()
            self.assertEqual(config.API_KEY, "testkey")

    def test_get_api_key_rcfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc_path = os.path.join(tmpdir, ".snowgloberc")
            with open(rc_path, "w") as f:
                f.write("SNOWGLOBE_API_KEY=rcfilekey\n")
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("os.getcwd", return_value=tmpdir):
                    config = Config()
                    self.assertEqual(config.API_KEY, "rcfilekey")

    def test_get_application_id_env(self):
        with mock.patch.dict(os.environ, {"SNOWGLOBE_APP_ID": "appid"}):
            with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                config = Config()
                self.assertEqual(config.APPLICATION_ID, "appid")

    def test_get_application_id_rcfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc_path = os.path.join(tmpdir, ".snowgloberc")
            with open(rc_path, "w") as f:
                f.write("SNOWGLOBE_APP_ID=rcappid\n")
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("os.getcwd", return_value=tmpdir):
                    with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                        config = Config()
                        self.assertEqual(config.APPLICATION_ID, "rcappid")

    def test_get_control_plane_url_env(self):
        with mock.patch.dict(os.environ, {"CONTROL_PLANE_URL": "http://env-url"}):
            with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                config = Config()
                self.assertEqual(config.CONTROL_PLANE_URL, "http://env-url")

    def test_get_control_plane_url_rcfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc_path = os.path.join(tmpdir, ".snowgloberc")
            with open(rc_path, "w") as f:
                f.write("CONTROL_PLANE_URL=http://rc-url\n")
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("os.getcwd", return_value=tmpdir):
                    with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                        config = Config()
                        self.assertEqual(config.CONTROL_PLANE_URL, "http://rc-url")

    def test_get_completions_per_interval_env(self):
        with mock.patch.dict(os.environ, {"COMPLETIONS_PER_SECOND": "42"}):
            with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                config = Config()
                self.assertEqual(config.CONCURRENT_COMPLETIONS_PER_INTERVAL, 42)

    def test_get_completions_per_interval_rcfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc_path = os.path.join(tmpdir, ".snowgloberc")
            with open(rc_path, "w") as f:
                f.write("COMPLETIONS_PER_SECOND=99\n")
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("os.getcwd", return_value=tmpdir):
                    with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                        config = Config()
                        self.assertEqual(config.CONCURRENT_COMPLETIONS_PER_INTERVAL, 99)

    def test_get_completions_interval_seconds_env(self):
        with mock.patch.dict(os.environ, {"COMPLETIONS_INTERVAL_SECONDS": "77"}):
            with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                config = Config()
                self.assertEqual(config.CONCURRENT_COMPLETIONS_INTERVAL_SECONDS, 77)

    def test_get_completions_interval_seconds_rcfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc_path = os.path.join(tmpdir, ".snowgloberc")
            with open(rc_path, "w") as f:
                f.write("COMPLETIONS_INTERVAL_SECONDS=88\n")
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("os.getcwd", return_value=tmpdir):
                    with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                        config = Config()
                        self.assertEqual(
                            config.CONCURRENT_COMPLETIONS_INTERVAL_SECONDS, 88
                        )

    def test_get_concurrent_risk_evaluations_env(self):
        with mock.patch.dict(os.environ, {"CONCURRENT_RISK_EVALUATIONS": "123"}):
            with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                config = Config()
                self.assertEqual(config.CONCURRENT_RISK_EVALUATIONS, 123)

    def test_get_concurrent_risk_evaluations_rcfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc_path = os.path.join(tmpdir, ".snowgloberc")
            with open(rc_path, "w") as f:
                f.write("CONCURRENT_RISK_EVALUATIONS=321\n")
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("os.getcwd", return_value=tmpdir):
                    with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                        config = Config()
                        self.assertEqual(config.CONCURRENT_RISK_EVALUATIONS, 321)

    def test_get_concurrent_risk_evaluations_interval_seconds_env(self):
        with mock.patch.dict(
            os.environ, {"CONCURRENT_RISK_EVALUATIONS_INTERVAL_SECONDS": "55"}
        ):
            with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                config = Config()
                self.assertEqual(
                    config.CONCURRENT_RISK_EVALUATIONS_INTERVAL_SECONDS, 55
                )

    def test_get_concurrent_risk_evaluations_interval_seconds_rcfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc_path = os.path.join(tmpdir, ".snowgloberc")
            with open(rc_path, "w") as f:
                f.write("CONCURRENT_RISK_EVALUATIONS_INTERVAL_SECONDS=66\n")
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("os.getcwd", return_value=tmpdir):
                    with mock.patch.dict(os.environ, {"SNOWGLOBE_API_KEY": "testkey"}):
                        config = Config()
                        self.assertEqual(
                            config.CONCURRENT_RISK_EVALUATIONS_INTERVAL_SECONDS, 66
                        )


if __name__ == "__main__":
    unittest.main()
