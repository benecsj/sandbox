Compiler Test Specification - oAW tests
========================================================================================================================

Bogus_oAW_Compiler_Tests
------------------------

.. sw_test:: Bogus_oAW_Compiler_Tests
   :id: TS_Bogus_oAW_Compiler_Tests
   :tst_shortdescription: Tests for successful Compile of Bogus
   :tst_level: Component Requirement Test
   :tst_designdoc: Bogus_VerificationDocumentation.docx
   :tst_envconditions: oAW on PC
   :tst_method: Interface tests/API tests
   :tst_preparation: nothing specific
   :tst_type: Manual
   :tst_env: Generator-Test
   :tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-6001, BSW_SEC_ModulesHere_Bogus-8001

   See descriptions below

   .. sw_test_step:: Bogus_Compile_KeyManagement
      :id: TSS_Bogus_oAW_Compiler_Tests_0001
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Bogus_oAW_Compiler_Tests_0002
      :collapse: true
      :tests: BSW_SEC_ModulesHere_Bogus-6001, BSW_SEC_ModulesHere_Bogus-8001

      Description: Ensures generated key management sources compile without errors.

      Input: Generated key management source files.

      Output: Successful compilation artifacts for key management.

   .. sw_test_step:: Bogus_Compile_Primitives
      :id: TSS_Bogus_oAW_Compiler_Tests_0003
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Bogus_oAW_Compiler_Tests_0004
      :collapse: true
      :tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-6001

      Description: Ensures generated bogus primitives compile without errors.

      Input: Generated bogus primitive sources.

      Output: Successful compilation artifacts without warnings treated as errors.
