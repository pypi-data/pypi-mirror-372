# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import abc
from typing import Optional

from dyff.schema import commands
from dyff.schema.commands import DyffCommandType, EntityIdentifier, FamilyIdentifier
from dyff.schema.platform import DyffEntityType, EntityStatus, EntityStatusReason


class CommandBackend(abc.ABC):
    """Base class for implementations of the Command model in our CQRS architecture.

    Implementations need to override close() and execute(). The other convenience
    methods are implemented in terms of execute().
    """

    @abc.abstractmethod
    def close(self) -> None:
        """Shut down the command backend cleanly."""

    @abc.abstractmethod
    def execute(self, command: DyffCommandType) -> None:
        """Execute a command."""

    def create_entity(self, entity: DyffEntityType) -> None:
        """Create a new entity in the system.

        :param enntity: Specification of the entity.
        """
        return self.execute(commands.CreateEntity(data=entity))

    def delete_entity(self, entity_identifier: EntityIdentifier) -> None:
        """Delete an existing entity.

        :param entity_identifier: The identifier of the entity to delete.
        """
        return self.update_status(
            entity_identifier,
            status=EntityStatus.deleted,
            reason=EntityStatusReason.delete_command,
        )

    def edit_entity_documentation(
        self,
        entity_identifier: EntityIdentifier,
        edit: commands.EditEntityDocumentationPatch,
    ) -> None:
        """Edit the documentation of an entity.

        To delete a field, set that field explicitly to ``None``. Fields that
        are not set explicitly remain unchanged.

        :param entity_identifier: The identifier of the entity to delete.
        :param edit: The documentation edits to apply.
        """
        return self.execute(
            commands.EditEntityDocumentation(
                data=commands.EditEntityDocumentationData(
                    kind=entity_identifier.kind,
                    id=entity_identifier.id,
                    attributes=commands.EditEntityDocumentationAttributes(
                        documentation=edit,
                    ),
                )
            )
        )

    def edit_entity_labels(
        self,
        entity_identifier: EntityIdentifier,
        edit: commands.EditEntityLabelsAttributes,
    ) -> None:
        """Edit the labels of a labeled entity.

        To delete a field, set that field explicitly to ``None``. Fields that
        are not set explicitly remain unchanged.

        :param entity_identifier: The identifier of the entity to delete.
        :param edit: The label edits to apply.
        """
        return self.execute(
            commands.EditEntityLabels(
                data=commands.EditEntityLabelsData(
                    kind=entity_identifier.kind,
                    id=entity_identifier.id,
                    attributes=edit,
                )
            )
        )

    def edit_family_members(
        self,
        family_identifier: FamilyIdentifier,
        edit: commands.EditFamilyMembersAttributes,
    ) -> None:
        """Edit the members of a Family.

        :param family_identifier: The identifier of the Family to edit.
        :param edit: The members edits to apply.
        """
        return self.execute(
            commands.EditFamilyMembers(
                data=commands.EditFamilyMembersData(
                    kind=family_identifier.kind,
                    id=family_identifier.id,
                    attributes=edit,
                )
            )
        )

    def forget_entity(self, entity_identifier: EntityIdentifier) -> None:
        """Forget an entity (remove all stored data permanently).

        :param entity_identifier: The identifier of the entity to forget.
        """
        return self.execute(commands.ForgetEntity(data=entity_identifier))

    def terminate_workflow(self, entity_identifier: EntityIdentifier) -> None:
        """Terminate a running workflow.

        .. deprecated:: 0.21.0

            The 'Terminate' status will be removed in a future version.

        :param entity_identifier: The identifier of the entity corresponding
            to the workflow to terminate.
        """
        return self.update_status(
            entity_identifier,
            status=EntityStatus.terminated,
            reason=EntityStatusReason.terminate_command,
        )

    def update_status(
        self,
        entity_identifier: EntityIdentifier,
        *,
        status: str,
        reason: Optional[str] = None,
    ) -> None:
        """Update the status of an entity.

        :param entity_identifier: The identifier of the entity to delete.
        :param status: New .status value
        :param reason: New .reason value
        """
        return self.execute(
            commands.UpdateEntityStatus(
                data=commands.UpdateEntityStatusData(
                    kind=entity_identifier.kind,
                    id=entity_identifier.id,
                    attributes=commands.UpdateEntityStatusAttributes(
                        status=status,
                        reason=reason,
                    ),
                )
            )
        )
