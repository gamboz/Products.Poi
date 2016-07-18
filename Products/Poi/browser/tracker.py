from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.PythonScripts.standard import url_quote
from ZTUtils import make_query

from plone import api

ACTIVE_STATES = ['open', 'in-progress', 'unconfirmed']


class IssueFolderView(BrowserView):

    issue_portal_type = 'Issue'

    def getActiveStates(self):
        return ACTIVE_STATES

    def getFilteredIssues(self, criteria=None, **kwargs):
        """Get the contained issues in the given criteria.
        """
        query = self.buildIssueSearchQuery(criteria, **kwargs)
        return api.content.find(**query)

    def getIssueSearchQueryString(self, criteria=None, **kwargs):
        """Return a query string for an issue query.

        Form of return string:name1=value1&name2=value2
        """
        query = self.buildIssueSearchQuery(criteria, **kwargs)
        return make_query(query)

    def buildIssueSearchQuery(self, criteria=None, **kwargs):
        """Build canonical query for issue search.
        """
        context = aq_inner(self.context)

        if criteria is None:
            criteria = kwargs
        else:
            criteria = dict(criteria)

        allowedCriteria = {
            'release': 'release',
            'area': 'area',
            'issueType': 'issue_type',
            'severity': 'severity',
            'targetRelease': 'target_release',
            'state': 'review_state',
            'tags': 'subject',
            'responsible': 'assignee',
            'creator': 'Creator',
            'text': 'SearchableText',
            'id': 'getId',
        }

        query = {}
        query['context'] = context
        query['portal_type'] = [self.issue_portal_type]

        for k, v in allowedCriteria.items():
            if criteria.get(k):
                query[v] = criteria[k]
            elif criteria.get(v):
                query[v] = criteria[v]

        # Playing nicely with the form.

        # Subject can be a string of one tag, a tuple of several tags
        # or a dict with a required query and an optional operator
        # 'and/or'.  We must avoid the case of the dict with only the
        # operator and no actual query, else we will suffer from
        # KeyErrors.  Actually, when coming from the
        # poi_issue_search_form, instead of say from a test, its type
        # is not 'dict', but 'instance', even though it looks like a
        # dict.  See http://plone.org/products/poi/issues/137
        if 'subject' in query:
            subject = query['subject']
            # We cannot use "subject.has_key('operator')" or
            # "'operator' in subject'" because of the strange
            # instance.
            try:
                subject['operator']
            except TypeError:
                # Fine: subject is a string or tuple.
                pass
            except KeyError:
                # No operator, so nothing can go wrong.
                pass
            else:
                try:
                    subject['query']
                except KeyError:
                    del query['subject']

        query['sort_on'] = criteria.get('sort_on', 'created')
        query['sort_order'] = criteria.get('sort_order', 'reverse')
        if criteria.get('sort_limit'):
            query['sort_limit'] = criteria.get('sort_limit')
        # allow substring searches
        if 'SearchableText' in query:
            query['SearchableText'] = '*{}*'.format(query['SearchableText'])

        return query

    def getMyIssues(self, openStates=['open', 'in-progress'],
                    memberId=None, manager=False):
        """Get a catalog query result set of my issues.

        So: all issues assigned to or submitted by the current user,
        with review state in openStates.

        If manager is True, add unconfirmed to the states.
        """
        if not memberId:
            memberId = api.user.get_current().id

        if manager:
            if 'unconfirmed' not in openStates:
                openStates += ['unconfirmed']

        issues = []

        for i in self.getFilteredIssues(state=openStates):
            assignee = i.assignee
            creator = i.Creator
            if memberId in (creator, assignee) or \
                    (manager and assignee == '(UNASSIGNED)'):
                issues.append(i)

        return issues

    def getOrphanedIssues(self, openStates=['open', 'in-progress'],
                          memberId=None):
        """Get a catalog query result set of orphaned issues.

        Meaning: all open issues not assigned to anyone and not owned
        by the given user.
        """
        if not memberId:
            memberId = api.user.get_current().id

        issues = []

        for i in self.getFilteredIssues(state=openStates):
            assignee = i.assignee
            creator = i.Creator
            if creator != memberId and not assignee:
                issues.append(i)

        return issues


class QuickSearchView(BrowserView):
    """Parse a quicksearch string and jump to the appropriate issue or
    search result page.

    """

    def __call__(self):
        tracker = aq_inner(self.context)
        search_text = self.request.form.get('searchText', '')
        issue_id = search_text
        if issue_id.startswith('#'):
            issue_id = issue_id[1:]
        base_url = tracker.absolute_url()
        if issue_id in tracker.keys():
            url = '%s/%s' % (base_url, issue_id)
        else:
            url = '%s/poi_issue_search?SearchableText=%s' % (
                base_url, url_quote(search_text))
        self.request.RESPONSE.redirect(url)
