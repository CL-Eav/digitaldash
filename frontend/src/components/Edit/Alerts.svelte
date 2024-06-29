<script lang="ts">
  import type { View } from "src/app";
  import PID from "./Elements/PID.svelte";

  export let view: View;

  function addAlert() {
    view.alerts = [
      ...view.alerts,
      {
        message: "",
        op: "",
        priority: "",
        unit: "",
        value: "",
      },
    ];
  }

  function removeAlert(index: number) {
    let tempArr = view.alerts;
    tempArr.splice(index, 1);

    view.alerts = tempArr;
  }
</script>

<h4>Alerts</h4>

<p>
  Configure custom alerts to appear when a specific parameter threshold is met.
</p>

<hr />

<div class="alertsContainer">
  {#each view.alerts as alert, i}
    <div class="alertContainer">
      <div class="input-group">
        <div class="col-12">
          <label class="label" for="alertMessage">Message</label>
          <input
            required
            value={alert.message}
            class="value form-control"
            type="text"
            name="alert-message-{i}"
          />
        </div>

        <div class="col-sm-6 col-12">
          <label class="label" for="alert-pid-{i}">Parameter</label>

          <PID
            inputName="alert-pid-{i}"
            unitName="alert-unit-{i}"
            pid={view.alerts[i].pid}
            unit={view.alerts[i].unit}
          />
        </div>

        <div class="col-sm-3 col-12">
          <label for="alert-op-{i}">Operand</label>
          <select
            required
            value={alert.op}
            name="alert-op-{i}"
            class="m-1 form-control"
          >
            <option value="">-</option>
            {#each ["=", ">", "<", ">=", "<="] as op}
              <option value={op}>
                {op}
              </option>
            {/each}
          </select>
        </div>

        <div class="col-sm-3 col-12">
          <label class="label" for="alertValue">Value</label>
          <input
            required
            value={alert.value}
            class="m-1 form-control"
            type="number"
            name="alert-value-{i}"
          />
        </div>



        <div class="col-6">
          <label class="label" for="alert-priority-{i}"
            >Priority <i>(Lower equals higher priority)</i></label
          >
          <input
            required
            value={alert.priority}
            class="value form-control"
            type="number"
            name="alert-priority-{i}"
          />
        </div>
      

      <div class="mt-3 m-3 btn">
        <button
          on:click={() => {
            removeAlert(i);
          }}
          class="form-control delete"
          type="button" 
          style="background-color: #ff4d4d; color: white"
          >Delete Alert
          </button>
      </div>
    </div>
  </div>
  <hr>
  {/each}

  <div class="row ">
    <button 
    type="button" 
    style="background-color: blue; color: white" 
    class="form-control btn btn-full-width" on:click={addAlert}
      >Add new alert</button
    >
  </div>
</div>
