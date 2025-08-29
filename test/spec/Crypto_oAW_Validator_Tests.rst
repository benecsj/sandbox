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
   :tests: BSW_SWCS_CryptoDriver_Crypto-5770 BSW_SWCS_CryptoDriver_Crypto-7001 BSW_SWCS_CryptoDriver_Crypto-7010
           BSW_SWCS_CryptoDriver_Crypto-7020 BSW_SWCS_CryptoDriver_Crypto-7030 BSW_SWCS_CryptoDriver_Crypto-7040
           BSW_SWCS_CryptoDriver_Crypto-7050 BSW_SWCS_CryptoDriver_Crypto-7060 BSW_SWCS_CryptoDriver_Crypto-7070
           BSW_SWCS_CryptoDriver_Crypto-7080 BSW_SWCS_CryptoDriver_Crypto-7090 BSW_SWCS_CryptoDriver_Crypto-7100
           BSW_SWCS_CryptoDriver_Crypto-7110 BSW_SWCS_CryptoDriver_Crypto-7120 BSW_SWCS_CryptoDriver_Crypto-7130
           BSW_SWCS_CryptoDriver_Crypto-7140 BSW_SWCS_CryptoDriver_Crypto-7150 BSW_SWCS_CryptoDriver_Crypto-7160
           BSW_SWCS_CryptoDriver_Crypto-7170 BSW_SWCS_CryptoDriver_Crypto-7180 BSW_SWCS_CryptoDriver_Crypto-7190
           BSW_SWCS_CryptoDriver_Crypto-7200 BSW_SWCS_CryptoDriver_Crypto-7210 BSW_SWCS_CryptoDriver_Crypto-7220

   See descriptions below

   .. sw_test_step:: Crypto_Validate_Config.tsc
      :id: TSS_Crypto_oAW_Validator_Tests_0001
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Crypto_oAW_Validator_Tests_0002
      :collapse: true
      :tests: BSW_SWCS_CryptoDriver_Crypto-5770 BSW_SWCS_CryptoDriver_Crypto-7001 BSW_SWCS_CryptoDriver_Crypto-7010
           BSW_SWCS_CryptoDriver_Crypto-7020 BSW_SWCS_CryptoDriver_Crypto-7030 BSW_SWCS_CryptoDriver_Crypto-7040
           BSW_SWCS_CryptoDriver_Crypto-7050 BSW_SWCS_CryptoDriver_Crypto-7060 BSW_SWCS_CryptoDriver_Crypto-7070
           BSW_SWCS_CryptoDriver_Crypto-7080 BSW_SWCS_CryptoDriver_Crypto-7090 BSW_SWCS_CryptoDriver_Crypto-7100
           BSW_SWCS_CryptoDriver_Crypto-7110 BSW_SWCS_CryptoDriver_Crypto-7120 BSW_SWCS_CryptoDriver_Crypto-7130
           BSW_SWCS_CryptoDriver_Crypto-7140 BSW_SWCS_CryptoDriver_Crypto-7150 BSW_SWCS_CryptoDriver_Crypto-7160
           BSW_SWCS_CryptoDriver_Crypto-7170 BSW_SWCS_CryptoDriver_Crypto-7180 BSW_SWCS_CryptoDriver_Crypto-7190
           BSW_SWCS_CryptoDriver_Crypto-7200 BSW_SWCS_CryptoDriver_Crypto-7210 BSW_SWCS_CryptoDriver_Crypto-7220
      
      Description: Validates configuration files for crypto modules.
      
      Input: Crypto module configuration set.

      Output: Validation report without errors.
