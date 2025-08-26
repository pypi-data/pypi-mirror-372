#if !defined(OS_TIMING_HOOKS_ARTI)
#define OS_TIMING_HOOKS_ARTI

/**********************************************************************************************************************
 *  GLOBAL DATA TYPES AND STRUCTURES
 *********************************************************************************************************************/
/*! arti_os_trace endcoding:
 *  [7:4]  : ThreadId (two bytes)
 *  [3]    : Bit 16 always written to 1 ("ValidOsWriteFlag)
 *  [2]    : OS State Enum ID
 *  [1:0]  : Core ID (one byte)
 *
 *  0000 80 00
 *  ---- -- --
 *    |  ||  |
 *    |  ||  \ CoreId
 *    |  ||
 *    |  |\ StateId 
 *    |  \  Bit 16 always written to 1 ("ValidOsWriteFlag)
 *    \ ThreadId (16-bit)
 *
 *  Reasoning (optiming code size, i.e. run-time overhead):
 *  Only the ThreadId requires a shift.
 *  StateId and ValidOsWriteFlag are constants, thus shift is handled by preprocessor.
 *  CoreId may be derived during run-time, thus another shift can be avoided by allocating it to the LSB.
 *
 **********************************************************************************************************************/
extern volatile unsigned int {{trace_variable}};

/**********************************************************************************************************************
 *  DEFINES
 *********************************************************************************************************************/
/** Bit 16 of art_os_trace is always written to 1 in order to identify a valid write of the OS (not by e.g. data init routine of C-startup). **/
#define ARTI_VALID_OS_SIGNALING 0x80
 
/** ARTI OS Task/ISR state transitions **/
/** AR_CP_OSARTI_TASK **/
#define ARTI_OSARTITASK_ACTIVATE     0
#define ARTI_OSARTITASK_START        1
#define ARTI_OSARTITASK_WAIT         2
#define ARTI_OSARTITASK_RELEASE      3
#define ARTI_OSARTITASK_PREEMPT      4
#define ARTI_OSARTITASK_TERMINATE    5
#define ARTI_OSARTITASK_RESUME       6
#define ARTI_OSARTITASK_CONTINUE     7
/** AR_CP_OSARTI_CAT2ISR  **/
#define ARTI_OSCAT2ISR_START         16
#define ARTI_OSCAT2ISR_STOP          17
#define ARTI_OSCAT2ISR_ACTIVATE      18
#define ARTI_OSCAT2ISR_PREEMPT       19
#define ARTI_OSCAT2ISR_RESUME        20
 
/**********************************************************************************************************************
 *  OS_VTH_SCHEDULE()
 *********************************************************************************************************************/
/*! \brief          Trace thread-switches, where thread stands for task or ISR
 *  \details        This hook routine allows external tools to trace all context switches from task to ISR and back as
 *                  well as between tasks and between ISRs. So external tools may visualize the information or measure
 *                  the execution time of tasks and ISRs.
 *                  Mind that measured execution time values may not reflect the worst case, which would be necessary
 *                  for schedulability analysis.
 *
 *                  Callers:
 *                    - Os_TraceThreadSwitch()
 *                    - Os_TraceThreadResetAndResume()
 *                    - Os_TraceThreadCleanupAndResume()
 *                    - Os_TraceThreadSuspendAndStart()
 *
 *  \param[in]      FromThreadId     The ID of the thread which has run until the switch
 *  \param[in]      FromThreadReason Represents the reason why the thread is no longer running:
 *                                   - \ref OS_VTHP_TASK_TERMINATION    1
 *                                   - \ref OS_VTHP_ISR_END             2
 *                                   - \ref OS_VTHP_TASK_WAITEVENT      4
 *                                   - \ref OS_VTHP_TASK_WAITSEMA       8
 *                                   - \ref OS_VTHP_THREAD_PREEMPT      16
 *  \param[in]      ToThreadId       The ID of the thread which will run from now on
 *  \param[in]      ToThreadReason   Represents the reason why the thread runs from now on:
 *                                   - \ref OS_VTHP_TASK_ACTIVATION     1
 *                                   - \ref OS_VTHP_ISR_START           2
 *                                   - \ref OS_VTHP_TASK_SETEVENT       4
 *                                   - \ref OS_VTHP_TASK_GOTSEMA        8
 *                                   - \ref OS_VTHP_THREAD_RESUME       16
 *                                   - \ref OS_VTHP_THREAD_CLEANUP      32
 *  \param[in]      CallerCoreId     The ID of the core where the thread switch occurs
 *
 *  \context        OS internal
 *
 *  \reentrant      TRUE for different cores.
 *  \synchronous    TRUE
 *
 *  \pre          Interrupts locked to TP lock level.
 *
 *  \trace          CREQ-115029
 *
 *********************************************************************************************************************/
#define OS_VTH_SCHEDULE(FromThreadId, FromThreadReason, ToThreadId, ToThreadReason, CallerCoreId)                                                       \
{                                                                                                                                                       \
    switch (FromThreadReason) {                                                                                                                         \
        case OS_VTHP_TASK_TERMINATION:                                                                                                                  \
            {{trace_variable}} = (FromThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_TERMINATE<<8) {{CallerCoreId}};   /* e.g. suspended */  \
            break;                                                                                                                                      \
        case OS_VTHP_ISR_END:                                                                                                                           \
            {{trace_variable}} = (FromThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSCAT2ISR_STOP<<8) {{CallerCoreId}};         /* e.g. suspended */  \
            break;                                                                                                                                      \
        case OS_VTHP_TASK_WAITEVENT:                                                                                                                    \
            {{trace_variable}} = (FromThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_WAIT<<8) {{CallerCoreId}};        /* e.g. waiting */    \
            break;                                                                                                                                      \
        case OS_VTHP_TASK_WAITSEMA:                                                                                                                     \
            {{trace_variable}} = (FromThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_WAIT<<8) {{CallerCoreId}};        /* e.g. waiting */    \
            break;                                                                                                                                      \
        case OS_VTHP_THREAD_PREEMPT:                                                                                                                    \
            {{trace_variable}} = (FromThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_PREEMPT<<8) {{CallerCoreId}};     /* e.g. ready */      \
            break;                                                                                                                                      \
        default:                                                                                                                                        \
            break;                                                                                                                                      \
    }                                                                                                                                                   \
    switch (ToThreadReason) {                                                                                                                           \
        case OS_VTHP_TASK_ACTIVATION:                                                                                                                   \
            {{trace_variable}} = (ToThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_START<<8) {{CallerCoreId}};         /* e.g. running */    \
            break;                                                                                                                                      \
        case OS_VTHP_ISR_START:                                                                                                                         \
            {{trace_variable}} = (ToThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSCAT2ISR_START<<8) {{CallerCoreId}};          /* e.g. running */    \
            break;                                                                                                                                      \
        case OS_VTHP_TASK_SETEVENT:                                                                                                                     \
            {{trace_variable}} = (ToThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_CONTINUE<<8) {{CallerCoreId}};      /* e.g. running */    \
            break;                                                                                                                                      \
        case OS_VTHP_TASK_GOTSEMA:                                                                                                                      \
            {{trace_variable}} = (ToThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_CONTINUE<<8) {{CallerCoreId}};      /* e.g. running */    \
            break;                                                                                                                                      \
        case OS_VTHP_THREAD_RESUME:                                                                                                                     \
            {{trace_variable}} = (ToThreadId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_RESUME<<8) {{CallerCoreId}};        /* e.g. running */    \
            break;                                                                                                                                      \
        case OS_VTHP_THREAD_CLEANUP:                                                                                                                    \
            break;                                                                                                                                      \
        default:                                                                                                                                        \
            break;                                                                                                                                      \
    }                                                                                                                                                   \
}


/**********************************************************************************************************************
 *  OS_VTH_ACTIVATION()
 *********************************************************************************************************************/
/*! \brief          Trace the activation of a task.
 *  \details        This hook is called on the caller core when that core has successfully performed the activation of
 *                  TaskId on the destination core. As this OS implementation always performs task activation on the
 *                  destination core, DestCoreId and CallerCoreId are always identical.
 *
 *                  Callers:
 *                    - Os_TraceTaskActivate()
 *
 *  \param[in]      TaskId       The ID of the task which is activated
 *  \param[in]      DestCoreId   The ID of the core where the task will be executed
 *  \param[in]      CallerCoreId The ID of the core where this hook is called
 *
 *  \context        OS internal
 *
 *  \reentrant      TRUE for different caller cores.
 *  \synchronous    TRUE
 *
 *  \pre            Interrupts locked to TP lock level.
 *  \trace          CREQ-115010
 *********************************************************************************************************************/
#define OS_VTH_ACTIVATION(TaskId, DestCoreId, CallerCoreId) \
{    {{trace_variable}} = (TaskId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_ACTIVATE<<8) {{DestCoreId}}; /* e.g. ready */ }


/**********************************************************************************************************************
 *  OS_VTH_SETEVENT()
 *********************************************************************************************************************/
/*! \brief          Trace the event setting on a task.
 *  \details        This hook is called on the CallerCore when that core has successfully performed the event
 *                  setting on the destination core. As this OS implementation always performs event setting on the
 *                  destination core, DestCoreId and CallerCoreId are always identical.
 *
 *                  Callers:
 *                    - Os_TraceTaskSetEvent()
 *
 *  \param[in]      TaskId       The ID of the task which receives this event
 *  \param[in]      EventMask    A bit mask with the events which have been set
 *  \param[in]      StateChanged
 *                   - !0: The task state has changed from WAITING to READY
 *                   -  0: The task state has not changed
 *  \param[in]      DestCoreId   The ID of the core where the task will be executed
 *  \param[in]      CallerCoreId The ID of the core where this hook is called
 *
 *  \context        OS internal
 *
 *  \reentrant      TRUE for different caller cores.
 *  \synchronous    TRUE
 *
 *  \pre            Interrupts locked to TP lock level.
 *
 *  \trace          CREQ-115028
 *
 *********************************************************************************************************************/
#define OS_VTH_SETEVENT(TaskId, EventMask, StateChanged, DestCoreId, CallerCoreId) \
{ \
    if(StateChanged) { \
        {{trace_variable}} = (TaskId<<16) | (ARTI_VALID_OS_SIGNALING<<8) | (ARTI_OSARTITASK_RELEASE<<8) {{DestCoreId}}; /* e.g. ready */ \
    } \
}

#endif /* OS_TIMING_HOOKS_ARTI */

/**********************************************************************************************************************
 *  END OF FILE: Os_TimingHooks_arti.h
 *********************************************************************************************************************/