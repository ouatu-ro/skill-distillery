import { helper } from "./helper"

// helper is mentioned here as documentation noise.
const noise = "helper appears in a string but is not a reference"

export interface Task {
  id: string
}

export type TaskId = Task["id"]

export enum TaskState {
  Ready = "ready",
}

export class TaskRunner {
  async run(task: Task): Promise<string> {
    return helper(task.id)
  }
}

export const buildTask = (id: TaskId): string => helper(id)
