from ._base import Base

__all__ = ["Groups"]


class Groups(Base):

    def unlink_ldap_group(self, remote_id):
        """Delete a link for LDAP group

        remote_id: Group GUID

        `Read in Mattermost API docs (groups - UnlinkLdapGroup) <https://developers.mattermost.com/api-documentation/#/operations/UnlinkLdapGroup>`_

        """
        return self.client.delete(f"/api/v4/ldap/groups/{remote_id}/link")

    def get_groups(self, params=None):
        """Get groups

        page: The page to select.
        per_page: The number of groups per page.
        q: String to pattern match the ``name`` and ``display_name`` field. Will return all groups whose ``name`` and ``display_name`` field match any of the text.
        include_member_count: Boolean which adds the ``member_count`` attribute to each group JSON object
        not_associated_to_team: Team GUID which is used to return all the groups not associated to this team
        not_associated_to_channel: Group GUID which is used to return all the groups not associated to this channel
        since: Only return groups that have been modified since the given Unix timestamp (in milliseconds). All modified groups, including deleted and created groups, will be returned.
        *Minimum server version*: 5.24

        filter_allow_reference: Boolean which filters the group entries with the ``allow_reference`` attribute set.

        `Read in Mattermost API docs (groups - GetGroups) <https://developers.mattermost.com/api-documentation/#/operations/GetGroups>`_

        """
        return self.client.get("""/api/v4/groups""", params=params)

    def create_group(self, options):
        """Create a custom group

        group: Group object to create.
        user_ids: The user ids of the group members to add.

        `Read in Mattermost API docs (groups - CreateGroup) <https://developers.mattermost.com/api-documentation/#/operations/CreateGroup>`_

        """
        return self.client.post("""/api/v4/groups""", options=options)

    def get_group(self, group_id):
        """Get a group

        group_id: Group GUID

        `Read in Mattermost API docs (groups - GetGroup) <https://developers.mattermost.com/api-documentation/#/operations/GetGroup>`_

        """
        return self.client.get(f"/api/v4/groups/{group_id}")

    def delete_group(self, group_id):
        """Deletes a custom group

        group_id: The ID of the group.

        `Read in Mattermost API docs (groups - DeleteGroup) <https://developers.mattermost.com/api-documentation/#/operations/DeleteGroup>`_

        """
        return self.client.delete(f"/api/v4/groups/{group_id}")

    def patch_group(self, group_id, options):
        """Patch a group

        group_id: Group GUID
        name:
        display_name:
        description:

        `Read in Mattermost API docs (groups - PatchGroup) <https://developers.mattermost.com/api-documentation/#/operations/PatchGroup>`_

        """
        return self.client.put(f"/api/v4/groups/{group_id}/patch", options=options)

    def restore_group(self, group_id):
        """Restore a previously deleted group.

        group_id: Group GUID

        `Read in Mattermost API docs (groups - RestoreGroup) <https://developers.mattermost.com/api-documentation/#/operations/RestoreGroup>`_

        """
        return self.client.post(f"/api/v4/groups/{group_id}/restore")

    def link_group_syncable_for_team(self, group_id, team_id):
        """Link a team to a group

        group_id: Group GUID
        team_id: Team GUID

        `Read in Mattermost API docs (groups - LinkGroupSyncableForTeam) <https://developers.mattermost.com/api-documentation/#/operations/LinkGroupSyncableForTeam>`_

        """
        return self.client.post(f"/api/v4/groups/{group_id}/teams/{team_id}/link")

    def unlink_group_syncable_for_team(self, group_id, team_id):
        """Delete a link from a team to a group

        group_id: Group GUID
        team_id: Team GUID

        `Read in Mattermost API docs (groups - UnlinkGroupSyncableForTeam) <https://developers.mattermost.com/api-documentation/#/operations/UnlinkGroupSyncableForTeam>`_

        """
        return self.client.delete(f"/api/v4/groups/{group_id}/teams/{team_id}/link")

    def link_group_syncable_for_channel(self, group_id, channel_id):
        """Link a channel to a group

        group_id: Group GUID
        channel_id: Channel GUID

        `Read in Mattermost API docs (groups - LinkGroupSyncableForChannel) <https://developers.mattermost.com/api-documentation/#/operations/LinkGroupSyncableForChannel>`_

        """
        return self.client.post(f"/api/v4/groups/{group_id}/channels/{channel_id}/link")

    def unlink_group_syncable_for_channel(self, group_id, channel_id):
        """Delete a link from a channel to a group

        group_id: Group GUID
        channel_id: Channel GUID

        `Read in Mattermost API docs (groups - UnlinkGroupSyncableForChannel) <https://developers.mattermost.com/api-documentation/#/operations/UnlinkGroupSyncableForChannel>`_

        """
        return self.client.delete(f"/api/v4/groups/{group_id}/channels/{channel_id}/link")

    def get_group_syncable_for_team_id(self, group_id, team_id):
        """Get GroupSyncable from Team ID

        group_id: Group GUID
        team_id: Team GUID

        `Read in Mattermost API docs (groups - GetGroupSyncableForTeamId) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupSyncableForTeamId>`_

        """
        return self.client.get(f"/api/v4/groups/{group_id}/teams/{team_id}")

    def get_group_syncable_for_channel_id(self, group_id, channel_id):
        """Get GroupSyncable from channel ID

        group_id: Group GUID
        channel_id: Channel GUID

        `Read in Mattermost API docs (groups - GetGroupSyncableForChannelId) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupSyncableForChannelId>`_

        """
        return self.client.get(f"/api/v4/groups/{group_id}/channels/{channel_id}")

    def get_group_syncables_teams(self, group_id):
        """Get group teams

        group_id: Group GUID

        `Read in Mattermost API docs (groups - GetGroupSyncablesTeams) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupSyncablesTeams>`_

        """
        return self.client.get(f"/api/v4/groups/{group_id}/teams")

    def get_group_syncables_channels(self, group_id):
        """Get group channels

        group_id: Group GUID

        `Read in Mattermost API docs (groups - GetGroupSyncablesChannels) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupSyncablesChannels>`_

        """
        return self.client.get(f"/api/v4/groups/{group_id}/channels")

    def patch_group_syncable_for_team(self, group_id, team_id, options):
        """Patch a GroupSyncable associated to Team

        group_id: Group GUID
        team_id: Team GUID
        auto_add:

        `Read in Mattermost API docs (groups - PatchGroupSyncableForTeam) <https://developers.mattermost.com/api-documentation/#/operations/PatchGroupSyncableForTeam>`_

        """
        return self.client.put(f"/api/v4/groups/{group_id}/teams/{team_id}/patch", options=options)

    def patch_group_syncable_for_channel(self, group_id, channel_id, options):
        """Patch a GroupSyncable associated to Channel

        group_id: Group GUID
        channel_id: Channel GUID
        auto_add:

        `Read in Mattermost API docs (groups - PatchGroupSyncableForChannel) <https://developers.mattermost.com/api-documentation/#/operations/PatchGroupSyncableForChannel>`_

        """
        return self.client.put(f"/api/v4/groups/{group_id}/channels/{channel_id}/patch", options=options)

    def get_group_users(self, group_id, params=None):
        """Get group users

        group_id: Group GUID
        page: The page to select.
        per_page: The number of groups per page.

        `Read in Mattermost API docs (groups - GetGroupUsers) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupUsers>`_

        """
        return self.client.get(f"/api/v4/groups/{group_id}/members", params=params)

    def delete_group_members(self, group_id, params):
        """Removes members from a custom group

        group_id: The ID of the group to delete.
        user_ids:

        `Read in Mattermost API docs (groups - DeleteGroupMembers) <https://developers.mattermost.com/api-documentation/#/operations/DeleteGroupMembers>`_

        """
        return self.client.delete(f"/api/v4/groups/{group_id}/members", params=params)

    def add_group_members(self, group_id, options):
        """Adds members to a custom group

        group_id: The ID of the group.
        user_ids:

        `Read in Mattermost API docs (groups - AddGroupMembers) <https://developers.mattermost.com/api-documentation/#/operations/AddGroupMembers>`_

        """
        return self.client.post(f"/api/v4/groups/{group_id}/members", options=options)

    def get_group_stats(self, group_id):
        """Get group stats

        group_id: Group GUID

        `Read in Mattermost API docs (groups - GetGroupStats) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupStats>`_

        """
        return self.client.get(f"/api/v4/groups/{group_id}/stats")

    def get_groups_by_channel(self, channel_id, params=None):
        """Get channel groups

        channel_id: Channel GUID
        page: The page to select.
        per_page: The number of groups per page.
        filter_allow_reference: Boolean which filters the group entries with the ``allow_reference`` attribute set.

        `Read in Mattermost API docs (groups - GetGroupsByChannel) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupsByChannel>`_

        """
        return self.client.get(f"/api/v4/channels/{channel_id}/groups", params=params)

    def get_groups_by_team(self, team_id, params=None):
        """Get team groups

        team_id: Team GUID
        page: The page to select.
        per_page: The number of groups per page.
        filter_allow_reference: Boolean which filters in the group entries with the ``allow_reference`` attribute set.
        include_member_count: Boolean which adds a ``member_count`` field to each group object.
        include_timezones: Boolean which adds timezone information for group members.
        include_total_count: Boolean which adds total count of groups in the response.
        include_archived: Boolean which includes archived groups in the response.
        filter_archived: Boolean which filters out archived groups from the response.
        filter_parent_team_permitted: Boolean which filters groups based on parent team permissions.
        filter_has_member: User ID to filter groups that have this member.
        include_member_ids: Boolean which adds member IDs to the group objects.
        only_syncable_sources: Boolean which includes groups from syncable sources.

        `Read in Mattermost API docs (groups - GetGroupsByTeam) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupsByTeam>`_

        """
        return self.client.get(f"/api/v4/teams/{team_id}/groups", params=params)

    def get_groups_associated_to_channels_by_team(self, team_id, params=None):
        """Get team groups by channels

        team_id: Team GUID
        page: The page to select.
        per_page: The number of groups per page.
        filter_allow_reference: Boolean which filters in the group entries with the ``allow_reference`` attribute set.
        paginate: Boolean to determine whether the pagination should be applied or not

        `Read in Mattermost API docs (groups - GetGroupsAssociatedToChannelsByTeam) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupsAssociatedToChannelsByTeam>`_

        """
        return self.client.get(f"/api/v4/teams/{team_id}/groups_by_channels", params=params)

    def get_groups_by_user_id(self, user_id):
        """Get groups for a userId

        user_id: User GUID

        `Read in Mattermost API docs (groups - GetGroupsByUserId) <https://developers.mattermost.com/api-documentation/#/operations/GetGroupsByUserId>`_

        """
        return self.client.get(f"/api/v4/users/{user_id}/groups")
