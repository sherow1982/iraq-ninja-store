const axios = require('axios');
const crypto = require('crypto');
const fs = require('fs');

// Read products
const products = JSON.parse(fs.readFileSync('products.json', 'utf8'));

// Read or create tracking file
let tracking = { lastIndex: -1 };
const trackingFile = 'tweet-tracking.json';

if (fs.existsSync(trackingFile)) {
  tracking = JSON.parse(fs.readFileSync(trackingFile, 'utf8'));
}

// Get next product
tracking.lastIndex = (tracking.lastIndex + 1) % products.length;
const product = products[tracking.lastIndex];

// Save tracking
fs.writeFileSync(trackingFile, JSON.stringify(tracking, null, 2));

// Function to create URL slug from product title and SKU
function createProductSlug(title, sku) {
  // Remove SKU prefix (A. or G.) and use lowercase
  const skuClean = sku.toLowerCase().replace(/^[ag]\./, '');
  
  // Convert title to URL-safe slug
  const titleSlug = title
    .trim()
    .replace(/\s+/g, '-')  // Replace spaces with hyphens
    .replace(/[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\-]/g, '')  // Keep only Arabic chars and hyphens
    .replace(/-+/g, '-')  // Replace multiple hyphens with single
    .replace(/^-|-$/g, '');  // Remove leading/trailing hyphens
  
  return `${titleSlug}-${skuClean}.html`;
}

// OAuth 1.0a signature generation
function generateOAuthSignature(method, url, params, consumerSecret, tokenSecret = '') {
  const paramString = Object.keys(params)
    .sort()
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');
  
  const signatureBaseString = `${method}&${encodeURIComponent(url)}&${encodeURIComponent(paramString)}`;
  const signingKey = `${encodeURIComponent(consumerSecret)}&${encodeURIComponent(tokenSecret)}`;
  
  return crypto
    .createHmac('sha1', signingKey)
    .update(signatureBaseString)
    .digest('base64');
}

// Twitter API v1.1 (for posting tweets)
async function postTweet(text) {
  const url = 'https://api.twitter.com/1.1/statuses/update.json';
  const method = 'POST';
  
  // Check if secrets are set
  if (!process.env.TWITTER_API_KEY) {
    throw new Error('TWITTER_API_KEY is not set in secrets');
  }
  if (!process.env.TWITTER_API_SECRET) {
    throw new Error('TWITTER_API_SECRET is not set in secrets');
  }
  if (!process.env.TWITTER_ACCESS_TOKEN) {
    throw new Error('TWITTER_ACCESS_TOKEN is not set in secrets');
  }
  if (!process.env.TWITTER_ACCESS_TOKEN_SECRET) {
    throw new Error('TWITTER_ACCESS_TOKEN_SECRET is not set in secrets');
  }
  
  const oauthParams = {
    oauth_consumer_key: process.env.TWITTER_API_KEY,
    oauth_token: process.env.TWITTER_ACCESS_TOKEN,
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_nonce: crypto.randomBytes(16).toString('hex'),
    oauth_version: '1.0',
    status: text
  };
  
  const signature = generateOAuthSignature(
    method,
    url,
    oauthParams,
    process.env.TWITTER_API_SECRET,
    process.env.TWITTER_ACCESS_TOKEN_SECRET
  );
  
  oauthParams.oauth_signature = signature;
  
  const authHeader = 'OAuth ' + Object.keys(oauthParams)
    .filter(key => key.startsWith('oauth_'))
    .map(key => `${encodeURIComponent(key)}="${encodeURIComponent(oauthParams[key])}"`)
    .join(', ');
  
  try {
    const response = await axios.post(url, 
      `status=${encodeURIComponent(text)}`,
      {
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );
    console.log('✅ Tweet posted successfully!');
    return response.data;
  } catch (error) {
    console.error('❌ Error posting tweet:');
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Error details:', JSON.stringify(error.response.data, null, 2));
      
      // Common error messages
      if (error.response.status === 403) {
        console.error('\n⚠️  403 Forbidden - Possible reasons:');
        console.error('1. Invalid API keys or Access tokens');
        console.error('2. App permissions not set correctly (need Read and Write)');
        console.error('3. Access tokens not generated after setting permissions');
        console.error('\nPlease check:');
        console.error('- Go to https://developer.x.com/');
        console.error('- Check App Permissions: Must be "Read and Write"');
        console.error('- Regenerate Access Token after changing permissions');
      }
    } else {
      console.error('Error message:', error.message);
    }
    throw error;
  }
}

// Generate hashtags from product title (first 2-3 meaningful words)
function generateHashtags(title) {
  const words = title.split(' ').filter(w => w.length > 3).slice(0, 3);
  return words.map(w => '#' + w.replace(/[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9]/g, '')).join(' ');
}

// Iraqi cities hashtags
const iraqCities = '#بغداد #البصرة #الموصل #أربيل #كربلاء #النجف #السليمانية #الأنبار #ديالى #ذي_قار #واسط #صلاح_الدين #بابل #كركوك #القادسية #ميسان #المثنى #دهوك';

// Create product URL using sitemap pattern
const productSlug = createProductSlug(product.title, product.sku);
const productUrl = `https://iraq-ninja-store.arabsad.com/products/${productSlug}`;
const productHashtags = generateHashtags(product.title);

const tweetText = `${product.title}\n\n${productUrl}\n\n${productHashtags} #العراق ${iraqCities}`;

console.log('📤 Preparing to post tweet...');
console.log('Product:', product.title);
console.log('URL:', productUrl);
console.log(`Tweet ${tracking.lastIndex + 1}/${products.length}`);

// Post tweet
postTweet(tweetText).then(() => {
  console.log(`\n✅ Successfully posted product ${tracking.lastIndex + 1}/${products.length}`);
}).catch(error => {
  console.error('\n❌ Failed to post tweet');
  process.exit(1);
});
