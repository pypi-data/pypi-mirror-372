class SyncGrades:
    """
    Define grades of synchronizers.

    The result of operational+configuration+slow grades should be all the
    synchronizers.
    """
    def partial_grades(self):
        """
        Return a list of synchronizers for resources that support partial syncs
        and that are useful to keep up-to-date at a high frequency.
        """
        return []

    def operational_grades(self):
        """
        Return a list of synchronizers for resources that change throughout a
        typical day. For example, tickets, service calls, notes, etc.

        Exclude resources that can potentially take a very long time to sync.
        """
        return []

    def configuration_grades(self):
        """
        Return a list of synchronizers for resources that change infrequently-
        such as on a weekly or monthly basis. For example, ticket types,
        statuses, priorities, etc.
        """
        return []

    def slow_grades(self):
        """
        Return a list of synchronizers for resources that can potentially take
        a very long time to sync. For example, notes, time entries, etc.
        """
        return []
