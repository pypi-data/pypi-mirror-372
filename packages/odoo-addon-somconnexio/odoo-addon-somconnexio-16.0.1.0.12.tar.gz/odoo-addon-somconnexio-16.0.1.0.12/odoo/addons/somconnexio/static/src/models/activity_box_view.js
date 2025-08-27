/** @odoo-module **/
import '@mail/models/activity_box_view';
import { registerPatch } from '@mail/model/model_core';
import { many } from '@mail/model/model_field';

registerPatch({
    name: 'ActivityBoxView',
    fields: {
        activityViews: {
            compute() {
                return this.chatter?.thread?.activities?.filter(activity => activity.state !== "done").map(activity => {
                    return { activity };
                }) || [];
            },
        },
    }
});
