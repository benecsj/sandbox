Compiler Test Specification - oAW tests
========================================================================================================================

Crypto_oAW_Compiler_Tests
-------------------------

.. sw_test:: Crypto_oAW_Compiler_Tests
   :id: TS_Crypto_oAW_Compiler_Tests
   :tst_shortdescription: Tests for successful Compile of Crypto
   :tst_level: Component Requirement Test
   :tst_designdoc: Crypto_VerificationDocumentation.docx
   :tst_envconditions: oAW on PC
   :tst_method: Interface tests/API tests
   :tst_preparation: nothing specific
   :tst_type: Manual
   :tst_env: Generator-Test
   :tests: BSW_SWCS_CryptoDriver_Crypto-5770 BSW_SWCS_CryptoDriver_Crypto-6001 BSW_SWCS_CryptoDriver_Crypto-8001

   See descriptions below

   .. sw_test_step:: Crypto_Compile_KeyManagement.tsc
      :id: TSS_Crypto_oAW_Compiler_Tests_0001
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Crypto_oAW_Compiler_Tests_0002
      :collapse: true
      :tests: BSW_SWCS_CryptoDriver_Crypto-6001 BSW_SWCS_CryptoDriver_Crypto-8001
      
      Description: Ensures generated key management sources compile without errors.
      
      Input: Generated key management source files.

      Output: Successful compilation artifacts for key management.

   .. sw_test_step:: Crypto_Compile_Primitives.tsc
      :id: TSS_Crypto_oAW_Compiler_Tests_0003
      :collapse: true

   .. sw_test_step:: 1
      :id: TSS_Crypto_oAW_Compiler_Tests_0004
      :collapse: true
      :tests: BSW_SWCS_CryptoDriver_Crypto-5770 BSW_SWCS_CryptoDriver_Crypto-6001
      
      Description: Ensures generated crypto primitives compile without errors.
      
      Input: Generated crypto primitive sources.

      Output: Successful compilation artifacts without warnings treated as errors.
