/**
 * @file {{ filename }}
 * @brief Configuration for SWAT.
 *
 * Configuration masks and offsets for software tracing. Use
 * in combination with software tracing buffer and observer
 * code.
 */
#ifndef {{ include_guard_str }}
#define {{ include_guard_str }}

#define SWAT_BUFFER_SLOT_COUNT   {{ slot_count }}u // Number of u32 slots in the buffer
#define SWAT_CMPSWP_MAX_RETRIES  {{ max_retries }}u // Maximum retries for cmpswp operations

_Static_assert(SWAT_BUFFER_SLOT_COUNT < 0x8000u, "Buffer slot count too high.");

typedef unsigned char swat_u8;
typedef unsigned short swat_u16;
typedef unsigned int swat_u32;
typedef unsigned long long swat_u64;
typedef int swat_i32;

_Static_assert(sizeof(swat_u8) == 1, "swat_u8 size error.");
_Static_assert(sizeof(swat_u16) == 2, "swat_u16 size error.");
_Static_assert(sizeof(swat_u32) == 4, "swat_u32 size error.");
_Static_assert(sizeof(swat_u64) == 8, "swat_u64 size error.");
_Static_assert(sizeof(swat_i32) == 4, "swat_i32 size error.");

#define SWAT_CONFIG_MAJOR_VERSION    {{ version.major }}
#define SWAT_CONFIG_MINOR_VERSION    {{ version.minor }}
#define SWAT_CONFIG_REVISION_VERSION {{ version.revision }}
#define SWAT_CONFIG_PATCH_VERSION    {{ version.patch }}
#define SWAT_CONFIG_INTERFACE_ID     {{ version.interface_id }}

/**
 * generic encoding:
 *
 * +------------+-------+-------+
 * | Field      | Offset| Size  |
 * +------------+-------+-------+
 * | type_id    |  {{ "{:2}".format(generic.type_id_offset) }}   |  {{ "{:2}".format(generic.type_id_size) }}   |
 * | core_id    |  {{ "{:2}".format(generic.core_id_offset) }}   |  {{ "{:2}".format(generic.core_id_size) }}   |
 * | timestamp  |  {{ "{:2}".format(generic.timestamp_offset) }}   |  {{ "{:2}".format(generic.timestamp_size) }}   |
 * +------------+-------+-------+
 */
#define SWAT_OBSERVER_TYPE_ID_MASK          {{ size_to_mask(generic.type_id_size) }}UL // size = {{ generic.type_id_size }}
#define SWAT_OBSERVER_TYPE_ID_OFFSET        {{ generic.type_id_offset }}UL
#define SWAT_OBSERVER_TYPE_ID_ENCODE(value) \
  ((swat_u32) ((value) & SWAT_OBSERVER_TYPE_ID_MASK) << SWAT_OBSERVER_TYPE_ID_OFFSET)

#define SWAT_OBSERVER_TYPE_ID_STATUS        0UL

#define SWAT_OBSERVER_CORE_MASK             {{ size_to_mask(generic.core_id_size) }}UL // size = {{ generic.core_id_size }}
#define SWAT_OBSERVER_CORE_OFFSET           {{ generic.core_id_offset }}UL
#define SWAT_OBSERVER_CORE_ENCODE(value)    \
  ((swat_u32) ((value) & SWAT_OBSERVER_CORE_MASK) << SWAT_OBSERVER_CORE_OFFSET)

{% if generic.timestamp_size == 32 %}
#define SWAT_TIMESTAMP_32BIT 1UL
#define SWAT_TIMESTAMP_ENCODE(value)        0UL
{% elif generic.timestamp_size == 16 %}
#define SWAT_TIMESTAMP_REDUCTION_SHIFT      {{ time_right_shift }}UL
#define SWAT_TIMESTAMP_MASK                 {{ size_to_mask(generic.timestamp_size) }}UL // size = {{ generic.timestamp_size}}
#define SWAT_TIMESTAMP_OFFSET               {{ generic.timestamp_offset }}UL
#define SWAT_TIMESTAMP_ENCODE(value)        \
  ((((value) >> SWAT_TIMESTAMP_REDUCTION_SHIFT) & SWAT_TIMESTAMP_MASK) << SWAT_TIMESTAMP_OFFSET)
{% else %}
{{ raise("SWAT timestamp size must be 16 or 32 bit.") }}
{% endif %}

#define SWAT_OBSERVER_U8_VALUE_MASK          0xffUL // size = 8
#define SWAT_OBSERVER_U8_VALUE_OFFSET        8UL
#define SWAT_OBSERVER_U8_VALUE_ENCODE(value) \
  ((swat_u32) ((value) & SWAT_OBSERVER_U8_VALUE_MASK) << SWAT_OBSERVER_U8_VALUE_OFFSET)

{% if microsar_thread %}
/**
 * MICROSAR thread encoding:
 *
 * +------------+-------+-------+
 * | Field      | Offset| Size  |
 * +------------+-------+-------+
 * | state      |  {{ "{:2}".format(microsar_thread.state_id_offset ) }}   |  {{ "{:2}".format(microsar_thread.state_id_size) }}   |
 * | thread_id  |  {{ "{:2}".format(microsar_thread.object_id_offset ) }}   |  {{ "{:2}".format(microsar_thread.object_id_size) }}   |
 * +------------+-------+-------+
 */
#define SWAT_MICROSAR_THREAD_STATE_MASK          {{ size_to_mask(microsar_thread.state_id_size) }}UL // size = {{ microsar_thread.state_id_size }}
#define SWAT_MICROSAR_THREAD_STATE_OFFSET        {{ microsar_thread.state_id_offset }}UL
#define SWAT_MICROSAR_THREAD_STATE_ENCODE(value) \
  (((value) & SWAT_MICROSAR_THREAD_STATE_MASK) << SWAT_MICROSAR_THREAD_STATE_OFFSET)

#define SWAT_MICROSAR_THREAD_ID_MASK          {{ size_to_mask(microsar_thread.object_id_size) }}UL // size = {{ microsar_thread.object_id_size}}
#define SWAT_MICROSAR_THREAD_ID_OFFSET        {{ microsar_thread.object_id_offset }}UL
#define SWAT_MICROSAR_THREAD_ID_ENCODE(value) \
  (((value) & SWAT_MICROSAR_THREAD_ID_MASK) << SWAT_MICROSAR_THREAD_ID_OFFSET)

#define SWAT_MICROSAR_THREAD_ID_AND_STATE_MASK \
  ((SWAT_MICROSAR_THREAD_STATE_MASK << SWAT_MICROSAR_THREAD_STATE_OFFSET) | \
   (SWAT_MICROSAR_THREAD_ID_MASK << SWAT_MICROSAR_THREAD_ID_OFFSET))
#define SWAT_MICROSAR_THREAD_ZERO_ID_AND_STATE(value) \
  ((value) & ~SWAT_MICROSAR_THREAD_ID_AND_STATE_MASK)

#define SWAT_OBSERVER_TYPE_ID_THREAD             {{ microsar_thread.type_id_key }}UL
{% else %}
// MICROSAR Thread tracing has not been configured!
#define SWAT_MICROSAR_THREAD_ID_ENCODE(value) (value)
#define SWAT_OBSERVER_TYPE_ID_THREAD          (0UL)
{% endif %}{# microsar_thread #}
{% if microsar_runnable %}

/**
 * MICROSAR Runnable encoding:
 *
 * +------------+-------+-------+
 * | Field      | Offset| Size  |
 * +------------+-------+-------+
 * | must be 0  |  {{ "{:2}".format(microsar_runnable.state_id_offset ) }}   |  {{ "{:2}".format(microsar_runnable.state_id_size) }}   |
 * | runnable_id|  {{ "{:2}".format(microsar_runnable.object_id_offset ) }}   |  {{ "{:2}".format(microsar_runnable.object_id_size) }}   |
 * +------------+-------+-------+
 */
#define SWAT_MICROSAR_RUNNABLE_ID_MASK          {{ size_to_mask(microsar_runnable.object_id_size) }}UL // size = {{ microsar_runnable.object_id_size }}
#define SWAT_MICROSAR_RUNNABLE_ID_OFFSET        {{ microsar_runnable.object_id_offset }}UL
#define SWAT_MICROSAR_RUNNABLE_ID_ENCODE(value) \
  (((value) & SWAT_MICROSAR_RUNNABLE_ID_MASK) << SWAT_MICROSAR_RUNNABLE_ID_OFFSET)

#define SWAT_OBSERVER_TYPE_ID_RUNNABLE          {{ microsar_runnable.type_id_key }}UL
{% else %}
// MICROSAR Runnable tracing has not been configured!
#define SWAT_MICROSAR_RUNNABLE_ID_ENCODE(value) (value)
#define SWAT_OBSERVER_TYPE_ID_RUNNABLE          (0UL)
{% endif %}{# microsar_runnable #}
{% for signal in signals %}

#define SWAT_OBSERVER_TYPE_ID_{{ signal.type_id_name.upper() }}          {{ signal.type_id_key }}UL
// To profile signal '{{ signal.type_id_name }}' add the following snippet to your code:
// SWAT_observe_u{{ signal.state_id_size }}({{ signal.type_id_name }}, SWAT_OBSERVER_TYPE_ID_{{ signal.type_id_name.upper() }});
{% endfor %}{# signals #}

#endif // {{ include_guard_str }}