/***************************************************************************
 *  FILE DESCRIPTION
 *  ------------------------------------------------------------------------
 *          File:  {{filename}}
 *
 *     Generator:  iTCHi 0.1 (iTCHi Trace Configuration Helper)
 *   Description:  VFB tracing hook TASKING implementation
 *    Created on:  {{date}}
 ***************************************************************************/

# include "Rte_Hook.h"

{% if instrumentation_type == "data_trace" %}
{% if trace_variable_definition %}
{{ trace_variable_definition }}
{% else %}
// Map variable into non-cached LMURAM on AURIX via TASKING compiler directive.
// volatile uint32 {{trace_variable}} __at(0xB0040200) = 0;
volatile uint32 {{trace_variable}} = 0;
{% endif %}
{% elif instrumentation_type == "stm_trace" %}
# define STM32_DTS(channel) *(volatile unsigned int*)({{stm_base_address}} + (channel*0x100))
# define STM_TRACE_RUNNABLE(value) do { STM32_DTS({{stm_channel}}) = value; } while(0)
{% elif instrumentation_type == "software_trace" %}
inline void isystem_profile_runnable(unsigned int val);

{% if sft_dbtag == true %}
inline void isystem_profile_runnable(unsigned int val)
{
    __asm volatile ("dbtag %0" :: "X" (val));  
}
{% else %}
inline void isystem_profile_runnable(unsigned int val)
{
    __asm volatile ("mov %0, r{{sft_dbpush_register}}" :: "X" (value) : "r{{sft_dbpush_register}}");
    __asm volatile ("dbpush r{{sft_dbpush_register}}-r{{sft_dbpush_register}}");
}
{% endif %}
{% elif instrumentation_type == "swat" %}
# include "swat_observer.h"
{% endif %}

{% if rte_hook_h.parts | length %}
# if (RTE_VFB_TRACE == 1)
{% endif %}
# define RTE_START_SEC_APPL_CODE
# include "Rte_MemMap.h"

{% if instrumentation_type in ["data_trace", "stm_trace"] %}
static inline uint8 get_core_id()
{
    /*
    On multi-core devices the instrumentation must include the core ID in the
    lower eight bits of the trace variable. The default instrumentation leaves
    these bits at zero. If you use a multi-core device you must change the function
    so that it returns the core ID.
    */
    // Begin Infineon AURIX core ID
    // uint8 core_id = __mfcr(0xFE1C); // Move core ID from core ID register (0xFE1C)
    // /** The CPU core 5 has the core register ID 6 which confuses all other tools.
    //  *  Therefore, we correct the core ID here. The if-statement should be compiled
    //  *  as a conditional move instruction and is therefore not too expensive.
    //  */
    // if (core_id == 6)
    // {
    //     core_id = 5;
    // }
    // return core_id;
    // End Infineon AURIX

    // Begin NVIDIA Orin core ID
    // const unsigned int c_AFF0_MASK    = 0x000000FF;
    // unsigned register int mpidrVal;
    // __asm("MRC  p15, 0, %0, c0, c0, 5": "=r" (mpidrVal));
    // char coreID = mpidrVal & c_AFF0_MASK;
    // return coreID;
    // End NVIDIA Orin

    // Add code for different multi-core arch here or leave as is for single-core.
    return 0;
}
{% endif %}

{% for hook in runnable_hooks %}
{{hook.declaration}}
{
{% if instrumentation_type == "data_trace" %}
    {{trace_variable}} = ({{hook.id}} << 8) | get_core_id();
{% elif instrumentation_type == "stm_trace" %}
    STM_TRACE_RUNNABLE({{hook.id}} << 8 | get_core_id());
{% elif instrumentation_type == "software_trace" %}
    isystem_profile_runnable({{hook.id}});
{% elif instrumentation_type == "swat" %}
    SWAT_observe_microsar_runnable((swat_u16) {{hook.id}}u);
{% endif %}
}

{% endfor %}

{% if rte_hook_h.parts | length %}
# endif
{% endif %}
