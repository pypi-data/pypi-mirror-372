# ifndef {{ include_guard_str }}
# define {{ include_guard_str }}

# include "swat_observer.h"

/**
 *  Content from OsInt.h parameter FromThreadReason:
 *
 *  OS_VTHP_TASK_TERMINATION   1
 *  OS_VTHP_ISR_END            2
 *  OS_VTHP_TASK_WAITEVENT     4
 *  OS_VTHP_TASK_WAITSEMA      8
 *  OS_VTHP_THREAD_PREEMPT    16
 *  
 *  Defined by us:
 *
 *  RUNNING                   32
 *  NEW                       64
 *  <UNUSED>                 128
 */
# define STATE_READY   (16)
# define STATE_RUNNING (32)
# define STATE_NEW     (64)

/**
 *  FromThreadId: Identifier of the thread (task, ISR) which has run on the caller core before theswitch took place
 *  FromThreadReason:
 *      - OS_VTHP_TASK_TERMINATION
 *      - OS_VTHP_ISR_END
 *      - OS_VTHP_TASK_WAITEVENT
 *      - OS_VTHP_TASK_WAITSEMA
 *      - OS_VTHP_THREAD_PREEMPT
 *  ToThreadId: The identifier of the thread, which runs from now on
 *  ToThreadReason: 
 *      - OS_VTHP_TASK_ACTIVATION
 *      - OS_VTHP_ISR_START
 *      - OS_VTHP_TASK_SETEVENT
 *      - OS_VTHP_GOTSEMA
 *      - OS_VTHP_THREAD_RESUME
 *  CallerCoreId: Identifier of the core which performs the thread switch
 */
#define OS_VTH_SCHEDULE(FromThreadId, FromThreadReason, ToThreadId, ToThreadReason, CallerCoreId) \
{\
  SWAT_observe_microsar_thread_schedule(((swat_u8) (FromThreadId)), ((swat_u8) (FromThreadReason)), \
                                        ((swat_u8) (ToThreadId)), ((swat_u8) (CallerCoreId))); \
}

/**
 *  TaskId: Identifier of the task which is activated
 *  DestCoreId: Identifier of the core on which the task is activated
 *  CallerCoreId: Identifier of the core which performs the activation
 *                (has called ActivateTask(), has called TerminateTask())
 */
#define OS_VTH_ACTIVATION(TaskId, DestCoreId, CallerCoreId) \
{ \
  SWAT_observe_microsar_thread(((swat_u8) (TaskId)), ((swat_u8) (STATE_NEW)), ((swat_u8) (DestCoreId))); \
}

/**
 *  TaskId: Identifier of the task which receives this event
 *  EventMask: A bit mask with the events which shall be set
 *  StateChanged: TRUE: The task state has changed from WAITING to READY
 *                FALSE: The task state hasnâ€™t changed
 *  DestCoreId: Identifier of the core on which the task receives the event
 *  CallerCoreId: Identifier of the core which performs the event setting
 */
#define OS_VTH_SETEVENT(TaskId, EventMask, StateChanged, DestCoreId, CallerCoreId) \
{ \
  if(StateChanged) \
  { \
    SWAT_observe_microsar_thread(((swat_u8) (TaskId)), ((swat_u8) (STATE_READY)), ((swat_u8) (DestCoreId))); \
  } \
}

# endif // {{ include_guard_str }}