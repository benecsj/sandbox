Generator Test Specification - oAW tests
========================================================================================================================

Bogus_oAW_Generator_Tests
-------------------------

.. sw_test:: Bogus_oAW_Generator_Tests
   :id: TS_Bogus_oAW_Generator_Tests
   :tst_shortdescription: Tests for successful Generate of Bogus
   :tst_level: Component Requirement Test
   :tst_designdoc: Bogus_VerificationDocumentation.docx
   :tst_envconditions: oAW on PC
   :tst_method: Interface tests/API tests
   :tst_preparation: nothing specific
   :tst_type: Manual
   :tst_env: Generator-Test
   :tests: BSW_SEC_ModulesHere_Bogus-5048, BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-8001,
           BSW_SEC_ModulesHere_Bogus-9001

   See descriptions below


   .. sw_test_step:: Bogus_Generate_KeyManagement
      :id: TSS_Bogus_oAW_Generator_Tests_0001
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Bogus_oAW_Generator_Tests_0002
      :collapse: true
      :tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-8001

      Description: Validates code generation for key management components.

      Input: Key management configuration set.

      Output: Generated key management sources and headers.


   .. sw_test_step:: Bogus_Generate_MultilineExample
      :id: TSS_Bogus_oAW_Generator_Tests_0003
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Bogus_oAW_Generator_Tests_0004
      :collapse: true
      :tests: BSW_SEC_ModulesHere_Bogus-5770, BSW_SEC_ModulesHere_Bogus-9001

      Description: This is a multi-line description for the generator test.
                   It spans multiple lines to validate parsing behavior.

      Input: First line of input description.
             Second line of input description.

      Output: First line of output description.
              Second line of output description.


   .. sw_test_step:: Bogus_Generate_Primitives
      :id: TSS_Bogus_oAW_Generator_Tests_0005
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Bogus_oAW_Generator_Tests_0006
      :collapse: true
      :tests: BSW_SEC_ModulesHere_Bogus-5048, BSW_SEC_ModulesHere_Bogus-5770

      Description: Validates code generation for basic bogus primitives
                   across supported targets.

      Input: Configurations for AES/HMAC primitive generation.

      Output: Generated source files and headers for primitives.


