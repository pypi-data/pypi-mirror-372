/**********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *  \verbatim
 *  Copyright (c) 2007 - 2020 by Vector Informatik GmbH.                                           All rights reserved.
 *
 *                 This software is copyright protected and proprietary to Vector Informatik GmbH.
 *                 Vector Informatik GmbH grants to you only those rights as set out in the license conditions.
 *                 All other rights remain with Vector Informatik GmbH.
 *  \endverbatim
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -------------------------------------------------------------------------------------------------------------------
 *         File:  {{filename}}
 *    Component:  MICROSAR Run-Time Interface TASKING
 *
 *  Description:  OS Vector Timing Hooks implementation file for timing measurements with TASKING winIDEA.
 *                For support, please submit a ticket at https://support.tasking.com.
 *                Use the keyword: "MICROSAR Run-Time Interface TASKING".
 *********************************************************************************************************************/
 
/**********************************************************************************************************************
 *  Infineon TriCore LMU Base Addresses(non_cached):
 *  For TC2XX
 *    TRACE32_TASKEVENT_BASE  0xB0000000
 *    TRACE32_RUNNABLE_BASE   0xB0000040
 *  
 *  For TC3XX
 *    TRACE32_TASKEVENT_BASE  0xB0040000
 *    TRACE32_RUNNABLE_BASE   0xB0040040
 *
 *  Infineon TriCore OLDA Base Addresses(non_cached):
 *  For TC3XX
 *    TRACE32_TASKEVENT_BASE  0xAFE00000
 *    TRACE32_RUNNABLE_BASE   0xAFE00008  
 *********************************************************************************************************************/

/**********************************************************************************************************************
 * DEFINES

/**********************************************************************************************************************
 *  GLOBAL DATA TYPES AND STRUCTURES
 *********************************************************************************************************************/
/*@@@vikafav @Date 2020-04-19 added memmap defines*/
#define TA_START_SEC_VAR_ZERO_INIT_UNSPECIFIED
#include "TA_MemMap.h"

volatile unsigned int {{trace_variable}};
volatile unsigned int arti_rte_trace;

#define TA_STOP_SEC_VAR_ZERO_INIT_UNSPECIFIED
#include "TA_MemMap.h"

/**********************************************************************************************************************
 *  END OF FILE: {{filename}}
 *********************************************************************************************************************/
