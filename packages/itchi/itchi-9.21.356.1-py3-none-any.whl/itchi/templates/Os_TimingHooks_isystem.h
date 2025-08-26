# ifndef {{ include_guard_str }}
# define {{ include_guard_str }}

{% if instrumentation_type == "data_trace" %}
# include "Std_Types.h"

extern volatile uint32 {{ trace_variable }};
{% elif instrumentation_type == "stm_trace" %}
#define STM32_DTS(channel) *(volatile unsigned int*)({{ stm_base_address }} + (channel*0x100))
#define STM_TRACE_OS(value) do { STM32_DTS({{ stm_channel }}) = value; } while(0)
{% elif instrumentation_type == "software_trace" %}
inline void isystem_profile_thread(unsigned int val)
{
    __asm volatile ("mov %0, r{{ sft_dbpush_register }}" :: "X" (val) : "r{{ sft_dbpush_register }}");
    __asm volatile ("dbpush r{{ sft_dbpush_register }}-r{{ sft_dbpush_register }}");
}
{% endif %}
{% if spinlock_generate_instrumentation %}
extern volatile uint32 {{ spinlock_trace_variable }};
{% endif %}

/*
    0x00 00 0000
      -- -- ----
      |  |     |
      |  |     \ TaskId
      |  |
      |  \ StateId
      |
      \ CoreId

    Content from isystemProfilerConfig.xml:
        <MaskID>0x0000FFFF</MaskID>
        <MaskState>0x00FF0000</MaskState>
        <MaskCore>0xFF000000</MaskCore>

*/
{% if software_based_coreid_gen %}
# define MASK_CORE(CoreId) ((0xff & CoreId) << 24)
{% else %}
# define MASK_CORE(CoreId) (0) // use core ID from hardware trace messages
{% endif %}
# define MASK_STATE(StateId) ((0xff & StateId) << 16)
# define MASK_STATE_RUNNING(StateId) ((0xff & (StateId | 0x1d)) << 16)
# define MASK_THREAD(ThreadId) (0xffff & ThreadId)

/*
    Content from OsInt.h parameter FromThreadReason:

    OS_VTHP_TASK_TERMINATION   1
    OS_VTHP_ISR_END            2
    OS_VTHP_TASK_WAITEVENT     4
    OS_VTHP_TASK_WAITSEMA      8
    OS_VTHP_THREAD_PREEMPT    16

    Content from profiler.xml:
        <Name>TypeEnum_TaskStateMapping</Name>
        <Enum><Name>NEW</Name><Value>11</Value></Enum>
        <Enum><Name>READY</Name><Value>16</Value></Enum>
        <Enum><Name>RUNNING</Name><Value>29</Value></Enum>
        <Enum><Name>RUNNING_ISR</Name><Value>31</Value></Enum>
        <Enum><Name>TERMINATED_TASK</Name><Value>1</Value></Enum>
        <Enum><Name>TERMINATED_ISR</Name><Value>2</Value></Enum>
        <Enum><Name>WAITING_EVENT</Name><Value>4</Value></Enum>
        <Enum><Name>WAITING_SEM</Name><Value>8</Value></Enum>

*/
# define STATE_NEW (11)
# define STATE_RUNNING (12)
# define STATE_READY (16)

/*
    FromThreadId Identifier of the thread (task, ISR) which has run on the caller core before theswitch took place
    FromThreadReason (OS_VTHP_TASK_TERMINATION, OS_VTHP_ISR_END, OS_VTHP_TASK_WAITEVENT, OS_VTHP_TASK_WAITSEMA, OS_VTHP_THREAD_PREEMPT
    ToThreadId The identifier of the thread, which runs from now on
    ToThreadReason (OS_VTHP_TASK_ACTIVATION, OS_VTHP_ISR_START, OS_VTHP_TASK_SETEVENT, OS_VTHP_GOTSEMA, OS_VTHP_THREAD_RESUME)
    CallerCoreId Identifier of the core which performs the thread switch

    We use MASK_STATE_RUNNING to change STATE to 29 for tasks, and 31 for ISRs. We achieve this
    by or'ing ToThreadReason with 0b0001'1101. OS_VTHP_ISR start is 0b0010. While the other reasons
    are for tasks and use of the remaining bits (0x000x'xx0x) each. That's why we get 0b1'1101 (29)
    for tasks and 0b1'1111 (31) for ISRs. The end result is that we can distinguish between a running
    task (29 = RUNNING) and a running ISR (31 = RUNNING_ISR).
*/
#define OS_VTH_SCHEDULE(FromThreadId, FromThreadReason, ToThreadId, ToThreadReason, CallerCoreId) \
{\
    {% if instrumentation_type == "data_trace" %}
    {{ trace_variable }} = MASK_CORE(CallerCoreId) | MASK_STATE(FromThreadReason) | MASK_THREAD(FromThreadId);\
    {{ trace_variable }} = MASK_CORE(CallerCoreId) | MASK_STATE_RUNNING(ToThreadReason) | MASK_THREAD(ToThreadId);\
    {% elif instrumentation_type == "stm_trace" %}
    STM_TRACE_OS(MASK_CORE(CallerCoreId) | MASK_STATE(FromThreadReason) | MASK_THREAD(FromThreadId));\
    STM_TRACE_OS(MASK_CORE(CallerCoreId) | MASK_STATE_RUNNING(ToThreadReason) | MASK_THREAD(ToThreadId));\
    {% elif instrumentation_type == "software_trace" %}
    isystem_profile_thread(MASK_CORE(CallerCoreId) | MASK_STATE(FromThreadReason) | MASK_THREAD(FromThreadId));\
    isystem_profile_thread(MASK_CORE(CallerCoreId) | MASK_STATE_RUNNING(ToThreadReason) | MASK_THREAD(ToThreadId));\
    {% endif %}
}

/*
    TaskId Identifier of the task which is activated
    DestCoreId Identifier of the core on which the task is activated
    CallerCoreId Identifier of the core which performs the activation (has called ActivateTask(), has called TerminateTask()
*/
#define OS_VTH_ACTIVATION(TaskId, DestCoreId, CallerCoreId) \
{% if instrumentation_type == "data_trace" %}
    {{ '{' + trace_variable }} = MASK_CORE(DestCoreId) | MASK_STATE(STATE_NEW) | MASK_THREAD(TaskId);}
{% elif instrumentation_type == "stm_trace" %}
    {STM_TRACE_OS(MASK_CORE(DestCoreId) | MASK_STATE(STATE_NEW) | MASK_THREAD(TaskId));}
{% elif instrumentation_type == "software_trace" %}
    {isystem_profile_thread(MASK_CORE(DestCoreId) | MASK_STATE(STATE_NEW) | MASK_THREAD(TaskId));}
{% endif %}

/*
    TaskId Identifier of the task which receives this event
    EventMask A bit mask with the events which shall be set
    StateChanged TRUE: The task state has changed from WAITING to READY
                 FALSE: The task state hasn’t changed
    DestCoreId Identifier of the core on which the task receives the event
    CallerCoreId Identifier of the core which performs the event setting (has called
*/
#define OS_VTH_SETEVENT(TaskId, EventMask, StateChanged, DestCoreId, CallerCoreId) \
{% if instrumentation_type == "data_trace" %}
    {if(StateChanged) {{ '{' + trace_variable }} = MASK_CORE(DestCoreId) | MASK_STATE(STATE_READY) | MASK_THREAD(TaskId);}}
{% elif instrumentation_type == "stm_trace" %}
    {if(StateChanged) {STM_TRACE_OS(MASK_CORE(DestCoreId) | MASK_STATE(STATE_READY) | MASK_THREAD(TaskId));}}
{% elif instrumentation_type == "software_trace" %}
    {if(StateChanged) {isystem_profile_thread(MASK_CORE(DestCoreId) | MASK_STATE(STATE_READY) | MASK_THREAD(TaskId));}}
{% endif %}


{% if spinlock_generate_instrumentation %}
// The following code is for instrumenting the Vector Spinlock Timing-Hooks
# define MASK_TYPE(TypeId) ((0xff & TypeId) << 16)

# define TYPE_REQ_SPINLOCK  0
# define TYPE_GOT_SPINLOCK  1
# define TYPE_REL_SPINLOCK  2
# define TYPE_REQ_ISPINLOCK 3
# define TYPE_GOT_ISPINLOCK 4
# define TYPE_REL_ISPINLOCK 5

#define OS_VTH_REQ_SPINLOCK(SpinlockId, CallerCoreId) \
{\
    {{ spinlock_trace_variable }} = MASK_CORE(CallerCoreId) | MASK_TYPE(TYPE_REQ_SPINLOCK) | SpinlockId;\
}

#define OS_VTH_REQ_ISSPINLOCK(SpinlockId, CallerCoreId) \
{\
    {{ spinlock_trace_variable }} = MASK_CORE(CallerCoreId) | MASK_TYPE(TYPE_REQ_ISPINLOCK) | SpinlockId;\
}

#define OS_VTH_GOT_SPINLOCK(SpinlockId, CallerCoreId) \
{\
    {{ spinlock_trace_variable }} = MASK_CORE(CallerCoreId) | MASK_TYPE(TYPE_GOT_SPINLOCK) | SpinlockId;\
}

#define OS_VTH_GOT_ISPINLOCK(SpinlockId, CallerCoreId) \
{\
    {{ spinlock_trace_variable }} = MASK_CORE(CallerCoreId) | MASK_TYPE(TYPE_GOT_ISPINLOCK) | SpinlockId;\
}

#define OS_VTH_REL_SPINLOCK(SpinlockId, CallerCoreId) \
{\
    {{ spinlock_trace_variable }} = MASK_CORE(CallerCoreId) | MASK_TYPE(TYPE_REL_SPINLOCK) | SpinlockId;\
}

#define OS_VTH_REL_ISSPINLOCK(SpinlockId, CallerCoreId) \
{\
    {{ spinlock_trace_variable }} = MASK_CORE(CallerCoreId) | MASK_TYPE(TYPE_REL_ISPINLOCK) | SpinlockId;\
}

{% endif %}
# endif // {{ include_guard_str }}