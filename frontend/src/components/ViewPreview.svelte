<script lang="ts">
    import Slider from "$components/Slider.svelte";
    import { enhance } from "$app/forms";
    import { getContext } from "svelte";
    import { keys } from "$lib/Keys";
    import { page } from "$app/stores";

    export let id: string;
    export let view: any;

    const { session } = getContext(keys.session);
    const KE_PIDS = $page.data.locals.constants.KE_PID;

    function handleFormSubmissionResults(result: any) {
        if (result?.data?.config) {
            $session.configuration = result.data.config;
        }

        result.data.id = $session.count;
        $session.actions = [result.data];
    }
</script>

<form
    method="POST"
    action="?/toggle_enabled"
    class="container col-sm-12 pr-4 pl-4"
    use:enhance={() => {
    return async ({ result }) => {
        handleFormSubmissionResults(result);
    };
    }}
>
    <input name="id" value={id} type="hidden" />
    <input
        name="config"
        value={JSON.stringify($session.configuration)}
        type="hidden"
    />
    
    <div class="row m-3">
        <div class="text-left col-6">
        <h5>{view.name}</h5>
        {#if view.default}
            (Default view)
        {/if}
        </div>

        <div class="text-right d-flex flex-row col-6">        
            <button
                class="slider-button"
                type="submit"
                data-toggle="tooltip"
                title="Enable/Disable this view"
            >
                <svelte:component this={Slider} {id} />
            </button>
        </div>
    </div>

    <a href="/edit/{id}">
        <div class="col-md-12 card transparent" style="width:500px">
        <img
            class="background-preview"
            src="images/Background/{view.background}"
            alt="view background {view.background}"
        />
    
        <div class="card-img-top">
            {#if view.gauges[0]}
                <img
                class="m-1 card-img-overlay" style=width:33%
                src="images/{view.gauges[0].theme}/preview.png"
                alt="gauge preview"
                />
            {/if}
        </div>

        <div class="card-img-top">
            {#if view.gauges[1]}
                <img
                class="m-1 card-img-overlay" style="left:33%; width:33%"
                src="images/{view.gauges[1].theme}/preview.png"
                alt="gauge preview"
                />
            {/if}
        </div>

        <div class="card-img-top">
            {#if view.gauges[2]}
            <img
            class="m-1 card-img-overlay" style="left:66%; width:33%"
            src="images/{view.gauges[2].theme}/preview.png"
            alt="gauge preview"
            />
            {/if}
        </div> 
<p></p>
        <!-- <div class="col-4 d-flex flex-column justify-content-center"> -->
            <div class="m-1 row">
            {#each view.gauges as gauge}
                {#if gauge && gauge.pid}
                <div class="col-4 text-center">
                    <p class="pid">
                    {KE_PIDS[gauge.pid]
                        ? KE_PIDS[gauge.pid].shortName
                        ? KE_PIDS[gauge.pid].shortName
                        : "Undefined"
                        : "Undefined"}
                    </p>
                </div>
                {/if}
            {/each}
            </div>
        </div>
    </a>
</form>

<style>
    img {
      border-radius: 25px;
      overflow: hidden;
    }
    .transparent {
      border: transparent;
      background-color: transparent;
    }
  
    .pid {
      background-color: #068efc;
      border-radius: 0.5em;
      padding: 2px;
      color: white;
      font-size: calc(75% + 1.0vw);
    }
  
  
    .background-preview {
      height: 9em;
    }
  
    .card {
      border-radius: 10px;
      padding: 0.5em;
      margin-top: 1em;
    }
    .slider-button {
      background: none;
      color: inherit;
      border: none;
      padding: 0;
      font: inherit;
      cursor: pointer;
      outline: inherit;
    }
  </style>
  