import os
import tempfile

from .io import invoke


class Interpreter(object):
    # Assuming whatever is called "js" on the path is likely to work best
    known_engines = ['js', 'rhino']

    def __init__(self, exes=None):
        engines = exes if exes else self.known_engines
        self.exe = self.detect(engines)

        if not self.exe:
            raise RuntimeError("No js engine could be found, tried: %s"
                               % ', '.join(engines))

    def detect(self, engines):
        found = None

        for engine in engines:
            # NOTE: Very platform specific
            success, stdout, stderr = invoke(['which', engine])
            exe = stdout

            # command exists, try executing a module on it
            if success:
                if self.run_test_module(exe):
                    found = exe
                    break

        return found

    def run_test_module(self, exe):
        (fd, filepath) = tempfile.mkstemp()
        try:
            content = (
                'try {'
                '  console.log(1 + 3);'  # node.js
                '} catch (e) {'
                '  if (e.name !== "ReferenceError") {'
                '    throw e;'
                '  }'
                '  print(1 + 3);'  # rhino/spidermonkey
                '}')
            os.write(fd, content)

            success, stdout, stderr = invoke([exe, filepath])
            if success and '4' == stdout.strip():
                return True
        finally:
            os.close(fd)
            os.unlink(filepath)

    def run_module(self, filepath):
        success, stdout, stderr = invoke([self.exe, filepath])
        return success, stderr
