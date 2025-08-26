{%- if instrumentation_type == "data_trace" -%}
#include "{{ vector_os_timing_hooks_h }}"

{% if trace_variable_definition %}
{{ trace_variable_definition }}
{% else %}
volatile uint32 {{ trace_variable }} = 0u;
{% endif %}
{% if spinlock_trace_variable_definition %}
{{ spinlock_trace_variable_definition }}
{% elif spinlock_trace_variable %}
volatile uint32 {{ spinlock_trace_variable }} = 0u;
{% endif %}

{% if not trace_variable_definition %}
// For Infineon AURIX micrcontrollers, map the trace variable into non-cached
// LMURAM to ensure that data writes are traceable via SRI bus trace.
// volatile uint32 {{ trace_variable }} __at(0xB0040100) = 0u;
{%- endif %}
{%- elif instrumentation_type == "stm_trace" -%}
// This file is not required for STM trace.
{%- elif instrumentation_type == "software_trace" -%}
// This file is not required for Software Trace.
{%- endif -%} {# instrumentation_type #}