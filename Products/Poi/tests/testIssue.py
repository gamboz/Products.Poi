#
# Skeleton ContextHelpTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc


class TestIssue(ptc.PoiTestCase):
    """Test issue functionality"""

    def afterSetUp(self):
        self.folder.invokeFactory('PoiTracker', 'tracker')
        self.tracker = self.folder.tracker
        self.tracker.invokeFactory('PoiIssue', '1')
        self.issue = self.tracker['1']

    def testEditIssue(self):
        pass

    def testNewWorkflowState(self):
        pass

    def testIsValid(self):
        pass

    def testRenameAfterCreation(self):
        pass

    def testSearchableText(self):
        pass

    def testUpdateResponses(self):
        pass

    def testManagersVocab(self):
        pass

    def testReleasesVocab(self):
        pass

    def testGetAvailableIssueTransactions(self):
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIssue))
    return suite

if __name__ == '__main__':
    framework()
