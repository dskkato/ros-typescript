/* eslint-disable @typescript-eslint/no-misused-promises */
/* eslint-disable jest/no-done-callback */

import http from "http";
import type { AddressInfo } from "net";

import { RosMasterClient } from "./RosMasterClient";

describe("RosMasterClient", () => {
  it("getPublishedTopics", (done) => {
    const server = http
      .createServer((_, res) => {
        res.writeHead(200, { "Content-Type": "text/xml" });
        const data = `<?xml version="1.0" encoding="UTF-8"?>
<methodResponse>
  <params>
    <param>
      <value>
        <array>
          <data>
            <value>
              <int>1</int>
            </value>
            <value>
              <string>current topics</string>
            </value>
            <value>
              <array>
                <data>
                  <value>
                    <array>
                      <data>
                        <value>
                          <string>/rosout</string>
                        </value>
                        <value>
                          <string>rosgraph_msgs/Log</string>
                        </value>
                      </data>
                    </array>
                  </value>
                  <value>
                    <array>
                      <data>
                        <value>
                          <string>/turtle1/pose</string>
                        </value>
                        <value>
                          <string>turtlesim/Pose</string>
                        </value>
                      </data>
                    </array>
                  </value>
                  <value>
                    <array>
                      <data>
                        <value>
                          <string>/turtle1/color_sensor</string>
                        </value>
                        <value>
                          <string>turtlesim/Color</string>
                        </value>
                      </data>
                    </array>
                  </value>
                  <value>
                    <array>
                      <data>
                        <value>
                          <string>/rosout_agg</string>
                        </value>
                        <value>
                          <string>rosgraph_msgs/Log</string>
                        </value>
                      </data>
                    </array>
                  </value>
                </data>
              </array>
            </value>
          </data>
        </array>
      </value>
    </param>
  </params>
</methodResponse>`;
        res.write(data);
        res.end();
      })
      .listen(undefined, "localhost", async () => {
        const port = (server.address() as AddressInfo).port;
        const client = new RosMasterClient(`http://localhost:${port}/`);
        const [status, msg, topics] = await client.getPublishedTopics("/test");
        expect(status).toEqual(1);
        expect(msg).toEqual("current topics");
        expect(topics).toEqual([
          ["/rosout", "rosgraph_msgs/Log"],
          ["/turtle1/pose", "turtlesim/Pose"],
          ["/turtle1/color_sensor", "turtlesim/Color"],
          ["/rosout_agg", "rosgraph_msgs/Log"],
        ]);
        server.close();
        done();
      });
  });
});
