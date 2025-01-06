import { Connection } from "./Connection";
import { RosFollowerClient } from "./RosFollowerClient";
import { Subscription } from "./Subscription";

// Handles a connection to a single publisher on a given topic.
export class PublisherLink {
  readonly connectionId: number;
  readonly subscription: Subscription;
  readonly rosFollowerClient: RosFollowerClient;
  readonly connection: Connection;

  constructor(
    connectionId: number,
    subscription: Subscription,
    rosFollowerClient: RosFollowerClient,
    connection: Connection,
  ) {
    this.connectionId = connectionId;
    this.subscription = subscription;
    this.rosFollowerClient = rosFollowerClient;
    this.connection = connection;
  }

  publisherXmlRpcUrl(): string {
    return this.rosFollowerClient.url();
  }
}
