import logging

logger = logging.getLogger(__name__)


class CallbacksHandler:
    api_client = None
    field_names = None
    ident_field = None
    base_callback_data = None

    def __init__(self):
        self.client = self.api_client()

    @property
    def needed_callbacks(self):
        raise NotImplementedError

    def _build_get_conditions(self):
        raise NotImplementedError

    def _build_post_data(self, callback):
        raise NotImplementedError

    def _post_register_processing(self, registered_callback):
        pass

    def _register_callback(self, callback):
        logger.info('Registering {} callback'.format(
            callback[self.ident_field]))
        registered_callback = self.client.create(
            self._build_post_data(callback))

        # Do anything else that needs to be done after registering a callback,
        #  depending on the PSA
        self._post_register_processing(registered_callback)

    def _delete_callback(self, callback):
        logger.info('Deleting callback {}'.format(callback['id']))
        self.client.delete(callback['id'])

    def _calculate_missing_unneeded_callbacks(self,
                                              needed_callbacks,
                                              current_callbacks):
        """
        Given the list of needed callbacks and current callbacks, figure out
        which callbacks need to be registered and which ones need to be
        removed.

        Returns a tuple of (need-to-add, need-to-remove) callbacks.
        """
        # For each current callback that matches a needed callback, delete it
        # from both needed and current.
        current_indexes_delete = set()
        needed_indexes_delete = set()

        # Add the index of the element to delete to a list, because it's
        # an error to delete elements out of a list while iterating through.
        for i_cur, current in enumerate(current_callbacks):
            for i_need, needed in enumerate(needed_callbacks):
                all_matched = True
                for field in self.field_names:
                    if current[field] != needed[field]:
                        # If any field doesn't match, don't delete the cb
                        all_matched = False
                if all_matched:
                    current_indexes_delete.add(i_cur)
                    needed_indexes_delete.add(i_need)
        for i_cur in reversed(sorted(current_indexes_delete)):
            # Delete from the end
            current_callbacks.pop(i_cur)
        for i_need in reversed(sorted(needed_indexes_delete)):
            # Delete from the end
            needed_callbacks.pop(i_need)

        return needed_callbacks, current_callbacks

    def get_callbacks(self):
        callbacks = self.client.get(**self._build_get_conditions())

        # Don't scan through any callbacks if they aren't ours
        cleaned_callbacks = self._clean_callbacks(callbacks)

        return cleaned_callbacks

    def get_needed_callbacks(self):
        """
        Return a list of callbacks
        """
        result = self.needed_callbacks
        for cb in result:
            cb['url'] = f"{self.settings['callback_root']}" \
                        f"{cb['url']}"

        return result

    def _clean_callbacks(self, callbacks):
        return callbacks

    def ensure_registered(self):
        """
        Do the minimum changes to ensure our callbacks are registered
        exactly once.
        """
        needed_callbacks = self.get_needed_callbacks()
        current_callbacks = self.get_callbacks()

        callbacks_to_add, callbacks_to_remove = \
            self._calculate_missing_unneeded_callbacks(
                needed_callbacks, current_callbacks
            )

        for callback in callbacks_to_add:
            self._register_callback(callback)
        for callback in callbacks_to_remove:
            self._delete_callback(callback)

    def ensure_deleted(self):
        """Do the needful to ensure our callbacks are gone."""
        callbacks = self.get_callbacks()

        for callback in callbacks:
            self._delete_callback(callback)
