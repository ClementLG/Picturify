
import unittest
import json
import sys
import os
import time

class JSONTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.results = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.results.append({
            'name': test._testMethodName,
            'description': test.shortDescription() or test._testMethodName,
            'status': 'PASS',
            'message': ''
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.results.append({
            'name': test._testMethodName,
            'description': test.shortDescription() or test._testMethodName,
            'status': 'FAIL',
            'message': str(err[1])
        })

    def addError(self, test, err):
        super().addError(test, err)
        self.results.append({
            'name': test._testMethodName,
            'description': test.shortDescription() or test._testMethodName,
            'status': 'ERROR',
            'message': str(err[1])
        })

class JSONTestRunner(unittest.TextTestRunner):
    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1, failfast=False, buffer=False, resultclass=JSONTestResult, warnings=None, *, tb_locals=False):
        super().__init__(stream, descriptions, verbosity, failfast, buffer, resultclass, warnings, tb_locals=tb_locals)

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

def run_tests_and_generate_report(start_dir='tests', file_pattern='test_*.py', output_file='tests/test_report.json'):
    # Calculate project root (parent of 'tests' directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure start_dir and output_file are absolute or correctly relative to root
    if not os.path.isabs(start_dir):
        start_dir = os.path.join(project_root, start_dir)
    if not os.path.isabs(output_file):
        output_file = os.path.join(project_root, output_file)
        
    loader = unittest.TestLoader()
    # Explicitly set top_level_dir to project root so 'tests' is recognized as a package
    suite = loader.discover(start_dir, pattern=file_pattern, top_level_dir=project_root)
    
    # Use a string buffer to suppress standard text output if desired, or just let it print to stderr
    # Here we let it print to stderr for immediate feedback while also collecting data
    runner = JSONTestRunner(verbosity=2)
    result = runner.run(suite)
    
    report = {
        'summary': {
            'total': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors),
            'failed': len(result.failures),
            'errors': len(result.errors),
            'duration': 'N/A' 
        },
        'results': result.results
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=4)
    
    print(f"\nTest report generated: {os.path.abspath(output_file)}")
    
    return not result.wasSuccessful()

if __name__ == '__main__':
    # Ensure project root is in path to import app, config, and tests package
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    start_time = time.time()
    failure = run_tests_and_generate_report()
    end_time = time.time()
    
    # We can update the report with duration if needed, but for now this is fine.
    
    sys.exit(1 if failure else 0)
