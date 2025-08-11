import benny from "benny";

import { parse } from "..";
import { testCases } from "./testCases";

async function main(): Promise<void> {
  for (const { name, msgDef } of testCases) {
    await benny.suite(
      name,
      benny.add("parse", () => {
        parse(msgDef);
      }),
      benny.cycle(),
      benny.complete(),
    );
  }
}

void main();
