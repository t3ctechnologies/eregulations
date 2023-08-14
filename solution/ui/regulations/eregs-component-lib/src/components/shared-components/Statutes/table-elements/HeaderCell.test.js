import flushPromises from "flush-promises";
import { render } from "@testing-library/vue";
import { describe, it, expect } from "vitest";

import statuteDatesFixture from "cypress/fixtures/statute-dates.json";

import { ssaSchema } from "../schemas/tableSchemas";

import HeaderCell from "./HeaderCell.vue";

describe("Statute Table Header Cell", () => {
    describe("SSA table header", () => {
        ssaSchema.forEach((column, index) => {
            it(`Creates a snapshot of header cell for column ${index + 1} without dates`, async () => {
                const wrapper = render(HeaderCell, {
                    props: {
                        cellData: column.header,
                        displayType: "table",
                    },
                });
                await flushPromises();
                expect(wrapper).toMatchSnapshot();
            });

            it(`Creates a snapshot of header cell for column ${index + 1} with dates`, async () => {
                const wrapper = render(HeaderCell, {
                    props: {
                        cellData: column.header,
                        displayType: "table",
                        columnDates: statuteDatesFixture,
                    },
                });
                await flushPromises();
                expect(wrapper).toMatchSnapshot();
            });
        });
    });
});
