<template>
    <v-list class="section-list">
        <v-list-item
            v-for="item in listItems"
            :key="item.identifier"
            :data-value="item.part + '-' + item.identifier"
            class="section-list-item"
            @click="clickMethod"
        >
            <span class="section-number">{{ item.label }} </span>
            <span class="section-text">{{ item.description }}</span>
        </v-list-item>
    </v-list>
</template>

<script>
export default {
    name: "SectionList",

    props: {
        filterEmitter: {
            type: Function,
            required: true,
        },
        listItems: {
            type: Array,
            required: true,
        },
        listId: {
            type: String,
            default: "",
        },
    },

    methods: {
        clickMethod(e) {
            this.filterEmitter({
                scope: "section",
                selectedIdentifier: e.currentTarget.dataset.value,
            });
        },
    },
};
</script>

<style lang="scss">
.section-list-item {
    display: inline-block;
    min-height: unset;
    padding-top: 5px;
    padding-bottom: 5px;
    font-size: 14px;

    .section-number {
        color: $dark_gray;
    }

    .section-text {
        color: $mid_gray;
    }
}
</style>
