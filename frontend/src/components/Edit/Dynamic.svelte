<script lang="ts">
  import type { View } from "src/app";
  import PID from "./Elements/PID.svelte";

  export let view: View;

  let enabled = view.dynamic.enabled || false;
</script>

<h4>Dynamic</h4>
<p>Configure when <i>this</i> view should be enabled.</p>
<hr />

<div class="dynamicContainer">
  <div class="row">
    <div class="col-sm-3 col-12">
      <div class="form-check">
        <input
          class="form-check-input"
          type="checkbox"
          bind:checked={enabled}
          name="dynamic-enabled"
          id="dynamic-enabled"
        />
        <label class="form-check-label" for="dynamic-enabled"> Enabled </label>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col-sm-6 col-12">
      <label for="dynamic-pid">Parameter</label>

      <PID
        inputName="dynamic-pid"
        unitName="dynamic-unit"
        pid={view.dynamic.pid}
        unit={view.dynamic.unit}
        {enabled}
      />
    </div>

    <div class="col-sm-3 col-12">
      <label for="dynamic-op">Operand</label>
      <select
        required
        disabled={!enabled}
        value={view.dynamic.op}
        name="dynamic-op"
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
      <label for="dynamic-value">Value</label>
      <input
        required
        disabled={!enabled}
        value={view.dynamic.value}
        class="m-1 form-control"
        type="number"
        name="dynamic-value"
      />
    </div>

    <div class="col-sm-6 col-12">
      <label for="dynamic-priority"
        >Priority <i>(Lower equals higher priority)</i></label
      >
      <input
        required
        disabled={!enabled}
        value={view.dynamic.priority}
        class="m-1 form-control"
        type="number"
        name="dynamic-priority"
      />
    </div>
  </div>
</div>
