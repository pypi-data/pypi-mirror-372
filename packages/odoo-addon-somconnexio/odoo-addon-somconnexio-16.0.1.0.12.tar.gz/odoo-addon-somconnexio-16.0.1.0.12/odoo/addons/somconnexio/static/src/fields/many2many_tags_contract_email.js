/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useOpenMany2XRecord } from "@web/views/fields/relational_utils";
import { sprintf } from "@web/core/utils/strings";

import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";
import { TagsList } from "@web/views/fields/many2many_tags/tags_list";

const { onMounted, onWillUpdateProps } = owl;

export class FieldMany2ManyContractTagsEmailTagsList extends TagsList {}
FieldMany2ManyContractTagsEmailTagsList.template = "FieldMany2ManyContractTagsEmailTagsList";

export class FieldMany2ManyContractTagsEmail extends Many2ManyTagsField {
    setup() {
        super.setup();

        this.openedDialogs = 0;
        this.recordsIdsToAdd = [];
        this.openMany2xRecord = useOpenMany2XRecord({
            resModel: this.props.relation,
            activeActions: {
                create: false,
                createEdit: false,
                write: false,
            },
            isToMany: true,
            fieldString: this.props.string,
        });
    }

    get tags() {
        // Add email to our tags
        const tags = super.tags;
        const emailByResId = this.props.value.records.reduce((acc, record) => {
            acc[record.resId] = record.data.email;
            return acc;
        }, {});
        tags.forEach(tag => tag.email = emailByResId[tag.resId]);
        return tags;
    }
};

FieldMany2ManyContractTagsEmail.components = {
    ...FieldMany2ManyContractTagsEmail.components,
    TagsList: FieldMany2ManyContractTagsEmailTagsList,
};

FieldMany2ManyContractTagsEmail.fieldsToFetch = Object.assign({},
    Many2ManyTagsField.fieldsToFetch,
    {email: {name: 'email', type: 'char'}}
);

FieldMany2ManyContractTagsEmail.additionalClasses = ["o_field_many2many_tags"];

registry.category("fields").add("many2many_tags_contract_email", FieldMany2ManyContractTagsEmail);

