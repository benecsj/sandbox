Generator Test Specification - oAW tests
========================================================================================================================

Crypto_oAW_Generator_Tests
--------------------------

.. sw_test:: Crypto_oAW_Generator_Tests
   :id: TS_Crypto_oAW_Generator_Tests
   :tst_shortdescription: Tests for successful Generate of Crypto
   :tst_level: Component Requirement Test
   :tst_designdoc: Crypto_VerificationDocumentation.docx
   :tst_envconditions: oAW on PC
   :tst_method: Interface tests/API tests
   :tst_preparation: nothing specific
   :tst_type: Manual
   :tst_env: Generator-Test
   :tests: BSW_SWCS_CryptoDriver_Crypto-5048 BSW_SWCS_CryptoDriver_Crypto-5770

   See descriptions below

   .. sw_test_step:: Crypto_Generate_Primitives.tsc
      :id: TSS_Crypto_oAW_Generator_Tests_0001
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Crypto_oAW_Generator_Tests_0002
      :collapse: true
      :tests: BSW_SWCS_CryptoDriver_Crypto-5048 BSW_SWCS_CryptoDriver_Crypto-5770
      
      Description: Validates code generation for basic crypto primitives
across supported targets.
      
      Input: Configurations for AES/HMAC primitive generation.

      Output: Generated source files and headers for primitives.
