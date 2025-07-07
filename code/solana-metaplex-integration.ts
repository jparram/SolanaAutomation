import { createUmi } from '@metaplex-foundation/umi-bundle-defaults';
import { mplTokenMetadata } from '@metaplex-foundation/mpl-token-metadata';
import { publicKey, generateSigner, percentAmount } from '@metaplex-foundation/umi';
import {
  createNft,
  fetchDigitalAsset,
  TokenStandard,
  Collection,
  CreateV1InstructionAccounts,
  CreateV1InstructionArgs,
  PrintSupply,
  Uses
} from '@metaplex-foundation/mpl-token-metadata';

/**
 * MetaplexClient provides high-level functionality to interact with Metaplex on Solana
 */
export class MetaplexClient {
  umi: any;
  connection: string;

  /**
   * Create a new MetaplexClient instance
   * 
   * @param rpcUrl - The Solana RPC endpoint URL
   * @param keypairOrWallet - A keypair or wallet adapter to use for transactions
   */
  constructor(rpcUrl: string, keypairOrWallet: any) {
    // Initialize Umi with the RPC endpoint
    this.umi = createUmi(rpcUrl).use(mplTokenMetadata());
    this.connection = rpcUrl;
    
    // Set the signer
    if (keypairOrWallet.secretKey) {
      // It's a keypair
      this.umi.identity = keypairOrWallet;
      this.umi.payer = keypairOrWallet;
    } else {
      // It's a wallet adapter
      this.umi.use({
        install(umi) {
          umi.identity = {
            publicKey: publicKey(keypairOrWallet.publicKey.toString()),
            signMessage: async (message) => {
              const signedMessage = await keypairOrWallet.signMessage(message);
              return signedMessage;
            },
            signTransaction: async (transaction) => {
              const signedTransaction = await keypairOrWallet.signTransaction(transaction);
              return signedTransaction;
            },
            signAllTransactions: async (transactions) => {
              const signedTransactions = await keypairOrWallet.signAllTransactions(transactions);
              return signedTransactions;
            },
          };
          umi.payer = umi.identity;
        }
      });
    }
  }

  /**
   * Create a new NFT
   * 
   * @param params - Parameters for NFT creation
   * @returns The transaction signature
   */
  async createNft(params: {
    name: string;
    symbol: string;
    uri: string;
    sellerFeeBasisPoints?: number;
    isCollection?: boolean;
    collection?: string;
    uses?: {
      useMethod: 'burn' | 'multiple' | 'single';
      remaining: number;
      total: number;
    };
  }) {
    try {
      // Generate a new mint address
      const mint = generateSigner(this.umi);
      
      // Prepare collection data if provided
      let collection: Collection | undefined = undefined;
      if (params.collection) {
        collection = {
          key: publicKey(params.collection),
          verified: false,
        };
      }
      
      // Prepare uses if provided
      let uses: Uses | undefined = undefined;
      if (params.uses) {
        const useMethod = 
          params.uses.useMethod === 'burn' ? { burn: {} } :
          params.uses.useMethod === 'multiple' ? { multiple: {} } :
          { single: {} };
        
        uses = {
          useMethod,
          remaining: BigInt(params.uses.remaining),
          total: BigInt(params.uses.total),
        };
      }
      
      // Create the NFT
      const result = await createNft(this.umi, {
        mint,
        name: params.name,
        symbol: params.symbol,
        uri: params.uri,
        sellerFeeBasisPoints: percentAmount(params.sellerFeeBasisPoints || 5),
        collection,
        uses,
        tokenStandard: params.isCollection 
          ? TokenStandard.NonFungible 
          : TokenStandard.NonFungible,
        decimals: 0,
        printSupply: { zero: {} } as PrintSupply,
      }).sendAndConfirm(this.umi);
      
      return {
        mint: mint.publicKey,
        signature: result.signature,
      };
    } catch (error) {
      console.error('Error creating NFT:', error);
      throw error;
    }
  }

  /**
   * Create a Programmable NFT (pNFT)
   * 
   * @param params - Parameters for pNFT creation
   * @returns The transaction signature
   */
  async createProgrammableNft(params: {
    name: string;
    symbol: string;
    uri: string;
    sellerFeeBasisPoints?: number;
    collection?: string;
    ruleSet?: string;
  }) {
    try {
      // Generate a new mint address
      const mint = generateSigner(this.umi);
      
      // Prepare collection data if provided
      let collection: Collection | undefined = undefined;
      if (params.collection) {
        collection = {
          key: publicKey(params.collection),
          verified: false,
        };
      }
      
      // Create the pNFT
      const result = await createNft(this.umi, {
        mint,
        name: params.name,
        symbol: params.symbol,
        uri: params.uri,
        sellerFeeBasisPoints: percentAmount(params.sellerFeeBasisPoints || 5),
        collection,
        tokenStandard: TokenStandard.ProgrammableNonFungible,
        ruleSet: params.ruleSet ? publicKey(params.ruleSet) : undefined,
        decimals: 0,
        printSupply: { zero: {} } as PrintSupply,
      }).sendAndConfirm(this.umi);
      
      return {
        mint: mint.publicKey,
        signature: result.signature,
      };
    } catch (error) {
      console.error('Error creating programmable NFT:', error);
      throw error;
    }
  }

  /**
   * Fetch NFT data by mint address
   * 
   * @param mintAddress - The mint address of the NFT
   * @returns The NFT data
   */
  async fetchNft(mintAddress: string) {
    try {
      const asset = await fetchDigitalAsset(this.umi, publicKey(mintAddress));
      return asset;
    } catch (error) {
      console.error('Error fetching NFT:', error);
      throw error;
    }
  }

  /**
   * Create a collection NFT
   * 
   * @param params - Parameters for collection NFT creation
   * @returns The transaction signature
   */
  async createCollectionNft(params: {
    name: string;
    symbol: string;
    uri: string;
    sellerFeeBasisPoints?: number;
  }) {
    return this.createNft({
      ...params,
      isCollection: true,
    });
  }

  /**
   * Mint an NFT with metadata from a URI
   * 
   * @param metadataUri - URI pointing to the NFT metadata
   * @param collectionMint - Optional collection mint address
   * @returns The transaction signature and mint address
   */
  async mintNftFromUri(metadataUri: string, collectionMint?: string) {
    try {
      // Fetch metadata from URI
      const response = await fetch(metadataUri);
      const metadata = await response.json();
      
      // Create NFT with metadata
      return this.createNft({
        name: metadata.name,
        symbol: metadata.symbol || metadata.name.substring(0, 4).toUpperCase(),
        uri: metadataUri,
        sellerFeeBasisPoints: metadata.seller_fee_basis_points || 500,
        collection: collectionMint,
      });
    } catch (error) {
      console.error('Error minting NFT from URI:', error);
      throw error;
    }
  }
}

/**
 * AI-assisted metadata generator for NFTs
 */
export class NFTMetadataGenerator {
  apiKey: string;
  endpoint: string;
  
  /**
   * Create a new NFTMetadataGenerator
   * 
   * @param apiKey - The API key for the AI service
   * @param endpoint - The endpoint for the AI service
   */
  constructor(apiKey: string, endpoint: string = 'https://api.openai.com/v1/chat/completions') {
    this.apiKey = apiKey;
    this.endpoint = endpoint;
  }
  
  /**
   * Generate NFT metadata from a prompt
   * 
   * @param prompt - Description of the NFT to generate
   * @returns The generated metadata
   */
  async generateMetadata(prompt: string): Promise<{
    name: string;
    description: string;
    attributes: Array<{ trait_type: string; value: string }>;
  }> {
    try {
      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "gpt-4o",
          messages: [
            {
              role: "system",
              content: "You are an expert NFT metadata generator. Given a prompt, generate complete, detailed NFT metadata including a name, description, and attributes."
            },
            {
              role: "user",
              content: `Generate NFT metadata for this concept: ${prompt}`
            }
          ],
          response_format: { type: "json_object" }
        })
      });
      
      const result = await response.json();
      const generatedContent = JSON.parse(result.choices[0].message.content);
      
      return {
        name: generatedContent.name,
        description: generatedContent.description,
        attributes: generatedContent.attributes || []
      };
    } catch (error) {
      console.error('Error generating NFT metadata:', error);
      throw error;
    }
  }
  
  /**
   * Generate image for an NFT
   * 
   * @param prompt - Description of the image to generate
   * @returns The generated image URL or base64 data
   */
  async generateImage(prompt: string): Promise<string> {
    try {
      const response = await fetch('https://api.openai.com/v1/images/generations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: "dall-e-3",
          prompt: prompt,
          n: 1,
          size: "1024x1024"
        })
      });
      
      const result = await response.json();
      return result.data[0].url;
    } catch (error) {
      console.error('Error generating NFT image:', error);
      throw error;
    }
  }
  
  /**
   * Create complete NFT metadata including image
   * 
   * @param prompt - Description of the NFT to generate
   * @returns Complete NFT metadata with image URL
   */
  async createCompleteNFTMetadata(prompt: string): Promise<any> {
    const metadata = await this.generateMetadata(prompt);
    const imageUrl = await this.generateImage(prompt);
    
    return {
      ...metadata,
      image: imageUrl,
      properties: {
        files: [
          {
            uri: imageUrl,
            type: "image/png"
          }
        ],
        category: "image",
        creators: []
      }
    };
  }
}

/**
 * Utility to upload NFT metadata to a storage provider
 */
export class NFTStorageUploader {
  apiKey: string;
  
  /**
   * Create a new NFTStorageUploader
   * 
   * @param apiKey - The API key for NFT.Storage
   */
  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }
  
  /**
   * Upload metadata to NFT.Storage
   * 
   * @param metadata - The metadata to upload
   * @returns The IPFS URI for the uploaded metadata
   */
  async uploadMetadata(metadata: any): Promise<string> {
    try {
      const response = await fetch('https://api.nft.storage/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(metadata)
      });
      
      const result = await response.json();
      if (!result.ok) {
        throw new Error(`Failed to upload: ${result.error?.message || 'Unknown error'}`);
      }
      
      // Return IPFS URI
      return `ipfs://${result.value.cid}`;
    } catch (error) {
      console.error('Error uploading metadata to NFT.Storage:', error);
      throw error;
    }
  }
  
  /**
   * Upload an image from URL to NFT.Storage
   * 
   * @param imageUrl - The URL of the image to upload
   * @returns The IPFS URI for the uploaded image
   */
  async uploadImageFromUrl(imageUrl: string): Promise<string> {
    try {
      // Fetch the image
      const imageResponse = await fetch(imageUrl);
      const imageBlob = await imageResponse.blob();
      
      // Upload to NFT.Storage
      const formData = new FormData();
      formData.append('file', imageBlob);
      
      const response = await fetch('https://api.nft.storage/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: formData
      });
      
      const result = await response.json();
      if (!result.ok) {
        throw new Error(`Failed to upload image: ${result.error?.message || 'Unknown error'}`);
      }
      
      // Return IPFS URI
      return `ipfs://${result.value.cid}`;
    } catch (error) {
      console.error('Error uploading image to NFT.Storage:', error);
      throw error;
    }
  }
  
  /**
   * Process and upload complete NFT data
   * 
   * @param metadata - Metadata with image URL
   * @returns The IPFS URI for the complete metadata
   */
  async processAndUploadNFT(metadata: any): Promise<string> {
    try {
      // 1. Upload the image to IPFS
      const imageUrl = metadata.image;
      const ipfsImageUri = await this.uploadImageFromUrl(imageUrl);
      
      // 2. Update metadata with IPFS image URI
      const updatedMetadata = {
        ...metadata,
        image: ipfsImageUri,
        properties: {
          ...metadata.properties,
          files: [
            {
              uri: ipfsImageUri,
              type: "image/png"
            }
          ]
        }
      };
      
      // 3. Upload metadata to IPFS
      return await this.uploadMetadata(updatedMetadata);
    } catch (error) {
      console.error('Error processing and uploading NFT:', error);
      throw error;
    }
  }
}

/**
 * Complete solution to generate, store, and mint NFTs using AI
 */
export class AIAssistedNFTMinter {
  metaplexClient: MetaplexClient;
  metadataGenerator: NFTMetadataGenerator;
  storageUploader: NFTStorageUploader;
  
  /**
   * Create a new AIAssistedNFTMinter
   * 
   * @param metaplexClient - MetaplexClient instance
   * @param openAIApiKey - OpenAI API key
   * @param nftStorageApiKey - NFT.Storage API key
   */
  constructor(
    metaplexClient: MetaplexClient,
    openAIApiKey: string,
    nftStorageApiKey: string
  ) {
    this.metaplexClient = metaplexClient;
    this.metadataGenerator = new NFTMetadataGenerator(openAIApiKey);
    this.storageUploader = new NFTStorageUploader(nftStorageApiKey);
  }
  
  /**
   * Generate and mint an NFT from a prompt
   * 
   * @param prompt - Description of the NFT to generate
   * @param collectionMint - Optional collection mint address
   * @returns The transaction signature and mint address
   */
  async generateAndMintNFT(prompt: string, collectionMint?: string) {
    try {
      // 1. Generate metadata and image with AI
      console.log("Generating NFT metadata and image...");
      const completeMetadata = await this.metadataGenerator.createCompleteNFTMetadata(prompt);
      
      // 2. Upload to IPFS
      console.log("Uploading to IPFS...");
      const metadataUri = await this.storageUploader.processAndUploadNFT(completeMetadata);
      
      // 3. Mint the NFT on Solana
      console.log("Minting NFT on Solana...");
      const { mint, signature } = await this.metaplexClient.createNft({
        name: completeMetadata.name,
        symbol: completeMetadata.name.substring(0, 4).toUpperCase(),
        uri: metadataUri.replace('ipfs://', 'https://ipfs.io/ipfs/'),
        sellerFeeBasisPoints: 500,
        collection: collectionMint,
      });
      
      return {
        mint,
        signature,
        metadata: completeMetadata,
        metadataUri
      };
    } catch (error) {
      console.error('Error in complete NFT minting process:', error);
      throw error;
    }
  }
}

// Example usage:
/*
// Create Metaplex client with wallet
const wallet = createKeypairFromSeed('your-seed-phrase');
const metaplexClient = new MetaplexClient('https://api.mainnet-beta.solana.com', wallet);

// Create AI-assisted minter
const nftMinter = new AIAssistedNFTMinter(
  metaplexClient,
  process.env.OPENAI_API_KEY,
  process.env.NFT_STORAGE_API_KEY
);

// Generate and mint an NFT
const result = await nftMinter.generateAndMintNFT('A futuristic city with flying cars and neon lights');
console.log(`NFT minted with address: ${result.mint.toString()}`);
*/
