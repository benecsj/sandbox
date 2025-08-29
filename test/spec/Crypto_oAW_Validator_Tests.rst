Validator Test Specification - oAW tests
========================================================================================================================

Crypto_oAW_Validator_Tests
--------------------------

.. sw_test:: Crypto_oAW_Validator_Tests
   :id: TS_Crypto_oAW_Validator_Tests
   :tst_shortdescription: Tests for successful Validate of Crypto
   :tst_level: Component Requirement Test
   :tst_designdoc: Crypto_VerificationDocumentation.docx
   :tst_envconditions: oAW on PC
   :tst_method: Interface tests/API tests
   :tst_preparation: nothing specific
   :tst_type: Manual
   :tst_env: Generator-Test
   :tests: BSW_SWCS_CryptoDriver_Crypto-7001 BSW_SWCS_CryptoDriver_Crypto-5770

   See descriptions below

   .. sw_test_step:: Crypto_Validate_Config.tsc
      :id: TSS_Crypto_oAW_Validator_Tests_0001
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Crypto_oAW_Validator_Tests_0002
      :collapse: true
      :tests: BSW_SWCS_CryptoDriver_Crypto-7001 BSW_SWCS_CryptoDriver_Crypto-5770
      
      Description: Validates configuration files for crypto modules.
      
      Input: Crypto module configuration set.

      Output: Validation report without errors.
