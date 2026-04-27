import { helper } from "./helper"

// helper is mentioned here as documentation noise.
const noise = "helper appears in a string but is not a reference"

export class TaskRunner {
  async run(task: { id: string }): Promise<string> {
    return helper(task.id)
  }
}

export const buildTask = (id: string): string => helper(id)
