
async function startSimulation(scenario, parameters) {
  const data = new URLSearchParams(
    Object.assign({scenario: scenario}, parameters)
  );
  const response = await fetch("/oemof/simulate", {
    method: "POST",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: data.toString(),
  });
  if (response.status === 200) {
    const json = await response.json();
    console.log(`Simulation started with task IDs: ${json.task_id}`);
    return json.task_id;
  } else {
    throw new Error(`Simulation not started. Response status: ${response.status}`);
  }
}

async function stopSimulation(taskId) {
  const data = new URLSearchParams({task_id: taskId});
  const response = await fetch("/oemof/terminate", {
    method: "POST",
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: data.toString(),
  });
  if (response.status === 200) {
    console.log(`Simulation stopped for taskId: ${taskId}`);
  } else {
    throw new Error(`Error terminating simulation with task ID '${taskId}'. Response status: ${response.status}`);
  }
}

async function checkSimulation(taskId) {
  const response = await fetch("/oemof/simulate?task_id=" + taskId, {
    method: "GET"
  });
  if (response.status === 200) {
    const json = await response.json();
    if (json.simulation_id !== null) {
      return json.simulation_id;
    }
    return null;
  }
  if (response.status === 400){
    const data = await response.json();
    throw new Error(data.msg);
  } else {
    throw new Error(`Error checking simulation with task ID '${taskId}'. Response status: ${response.status}`);
  }
}