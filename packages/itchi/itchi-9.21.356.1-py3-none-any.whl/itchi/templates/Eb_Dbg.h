/* =========================================================================
 OS task and ISR2 state tracing macro definitions for EB tresos AutoCore
 
 (c) TASKING 2023
 ========================================================================= */
#ifndef __DBG_H
#define __DBG_H

extern unsigned long {{ trace_variable_task }};
extern unsigned long {{ trace_variable_isr }};

/* Tasks */
#ifndef OS_TRACE_STATE_TASK
#define OS_TRACE_STATE_TASK(taskID, oldState, newState) \
    {{ trace_variable_task }} = (newState << 8) | (taskID);
#endif

/* ISR2s */
#ifndef OS_TRACE_STATE_ISR
#define OS_TRACE_STATE_ISR(isrID, oldState, newState) \
    {{ trace_variable_isr }} = (newState << 8) | (isrID);
#endif

#endif /* if !defined( DBG_H ) */
/*==================[end of file]===========================================*/
