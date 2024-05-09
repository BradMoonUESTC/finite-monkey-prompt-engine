// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {IVault} from "../interfaces/IVault.sol";

import {CNft, IERC721MetadataUpgradeable} from "./CNft.sol";

contract CBAYC is CNft {
    function initialize(IERC721MetadataUpgradeable _bayc) public initializer {
        __CNft_init(_bayc, "Certi BAYC", "cBAYC");
    }
}
