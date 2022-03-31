// SPDX-Licence-Identifier: MIT

pragma solidity 0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract AdvancedCollectible is ERC721, VRFConsumerBase {
    uint256 public tokenCounter;
    bytes32 public keyhash;
    uint256 public fee;
    enum Breed{PUG, SHIBA_INU, ST_BERNARD}
    mapping(bytes32 => address) public requestIdToSender;
    mapping(uint256 => Breed) public tokenIdToBreed;
    event requestedCollectible(bytes32 indexed requestId, address requester);
    event breedAssigned(uint256 indexed tokenId, Breed breed);

    constructor(address _vrfCoordinator, address _linkToken, bytes32 _keyHash, uint256 _fee) public
    VRFConsumerBase(_vrfCoordinator, _linkToken)
    ERC721("Dogie", "DOG")
    {
        tokenCounter = 0;
        keyhash = _keyHash;
        fee = _fee;
    }

    function createCollectible() public returns(bytes32) {
        bytes32 requestId = requestRandomness(keyhash, fee);
        requestIdToSender[requestId] = msg.sender;  // to store the original caller of the createCollectible() for fullfillRandomness()._safeMint() 
        emit requestedCollectible(requestId, msg.sender);
    }

    // 'internal' as only VRFCoordinator can call fulfillRandomness
    // 'override'
    function fulfillRandomness(bytes32 requestId, uint256 randomNumber) internal override {
        // assign a randomly 'breed' via randomNumber requested from VRFCoordinator; 
        // where do we get 'randomNumber'?
        Breed breed = Breed(randomNumber % 3);
        // create 'newTokenId' by assigning 'tokenCounter' value to it  
        uint256 newTokenId = tokenCounter;
        // by mapping, assign 'breed' to newly set 'newTokenId'    
        tokenIdToBreed[newTokenId] = breed;
        // and emit event    
        emit breedAssigned(newTokenId, breed);
        // msg.sender cannot be assigned to '_safeMint' function, as msg.sender is VRFCoordinator,
        // thus assign to 'owner' the address of a createCollectible() caller from mapping;
        address owner = requestIdToSender[requestId];
        // and mint NFT;  
        _safeMint(owner, newTokenId);
        // _setTokenURI(newTokenId, tokenURI) should follow, but it is created below;
        // increase tokenCounter value by one
        tokenCounter = tokenCounter + 1;    
    }

    function setTokenURI(uint256 tokenId, string memory _tokenURI) public {
        // reciprocate onchain metadata with the offchain data (pug, shiba inu, st bernard pictures)
        // only Owner can set token URI
        // _isApprovedOrOwner() and _msgSender() are imported from OpenZepellin contracts (ERC721)
        require(_isApprovedOrOwner(_msgSender(), tokenId),
         "ERC721: caller is not owner nor approved");
        _setTokenURI(tokenId, _tokenURI);
    }

}