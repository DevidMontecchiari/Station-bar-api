"""Run: python -m unittest discover -s checks -p test_class_start.py

Temporary files and owned HTTP servers only; no downloads or application data.
"""
import contextlib
import io
from pathlib import Path
import socket
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from start_class import ClassSession, Service, requirement_files, show_links


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class LauncherChecks(unittest.TestCase):
    def test_occupied_port_is_left_running_and_no_child_started(self):
        with tempfile.TemporaryDirectory() as folder, socket.socket() as existing:
            existing.bind(("127.0.0.1", 0))
            existing.listen()
            port = existing.getsockname()[1]
            session = ClassSession(Path(folder), [Service("existing", port, [sys.executable])])
            with self.assertRaisesRegex(RuntimeError, "already in use"):
                session.start()
            self.assertEqual(session.children, [])
            self.assertFalse(session.log_dir.exists())
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                pass

    def test_failed_second_service_cleans_up_first_and_keeps_data(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stored = root / "keep.json"
            stored.write_text('{"order": 123}', encoding="utf-8")
            first, second = free_port(), free_port()
            while second == first:
                second = free_port()
            planned = [Service("first", first, [sys.executable, "-m", "http.server", str(first), "--bind", "127.0.0.1"]),
                       Service("broken", second, [sys.executable, "-c", "raise SystemExit('deliberate startup failure')"])]
            session = ClassSession(root, planned)
            with self.assertRaisesRegex(RuntimeError, "deliberate startup failure"):
                session.start()
            self.assertTrue(all(p.poll() is not None for _,p,_,_ in session.children))
            self.assertTrue(all(log.closed for _,_,log,_ in session.children))
            self.assertEqual(stored.read_text(), '{"order": 123}')
            self.assertIn("deliberate startup failure", (session.log_dir / f"{second}.log").read_text())
            session.close()

    def test_local_and_codespaces_links_point_to_the_right_paths(self):
        planned = [Service("SQLite", 8002, [], "/docs")]
        for env, wanted in [({}, "http://127.0.0.1:8002/docs"),
            ({"CODESPACE_NAME":"example", "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN":"app.github.dev"},
             "https://example-8002.app.github.dev/docs")]:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                show_links(planned, env)
            self.assertIn(wanted, output.getvalue())

    def test_requirements_include_is_bounded_and_cycles_do_not_loop(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            a, b = root / "a.txt", root / "b.txt"
            a.write_text("-r b.txt\n")
            b.write_text("-r a.txt\n")
            self.assertEqual(len(requirement_files(root, a)), 2)
            b.write_text("-r ../outside.txt\n")
            with self.assertRaisesRegex(RuntimeError, "outside this repository"):
                requirement_files(root, a)


if __name__ == "__main__":
    unittest.main()
