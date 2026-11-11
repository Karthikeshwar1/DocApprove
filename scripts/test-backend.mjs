// Runs the Django tests with a Python that has the dependencies installed.
// Picks, in order: $PYTHON, backend/.venv, then `python` on PATH.
import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const backend = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'backend')
const venvPython = path.join(backend, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python')
const python = process.env.PYTHON || (existsSync(venvPython) ? venvPython : 'python')

const hasDeps = spawnSync(python, ['-c', 'import django, rest_framework'], { stdio: 'ignore' }).status === 0
if (!hasDeps) {
  console.error(
    `\nCannot run backend tests: "${python}" has no Django/DRF installed.\n` +
      'Activate the Python environment you installed backend/requirements.txt into,\n' +
      'or point PYTHON at its interpreter (e.g. PYTHON=/path/to/python npm test).\n',
  )
  process.exit(1)
}

const result = spawnSync(python, ['manage.py', 'test'], { cwd: backend, stdio: 'inherit' })
process.exit(result.status ?? 1)
