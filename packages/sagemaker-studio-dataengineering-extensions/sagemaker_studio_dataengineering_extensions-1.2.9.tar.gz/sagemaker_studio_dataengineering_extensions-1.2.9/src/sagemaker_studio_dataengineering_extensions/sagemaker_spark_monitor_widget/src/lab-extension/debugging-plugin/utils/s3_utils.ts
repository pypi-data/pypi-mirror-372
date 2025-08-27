const AWS = require('aws-sdk');
import { Credentials } from "aws-sdk";
import { SageMakerConnectionDetails } from "./jupyter_api_client"

function parseS3Url(s3Url: string): { bucket: string; key: string }  {
  const s3UrlRe = /^[sS]3:\/\/(.*?)\/(.*)/;

  let match = s3Url.match(s3UrlRe);
  if (match) {
    return {
      bucket: match[1],
      key: match[2],
    };
  }
  throw new Error("Invalid s3 url");
}

export async function  generatePresignedUrl(connectionDetail: SageMakerConnectionDetails,
                                            s3Location: string): Promise<any> {
  let s3Params = parseS3Url(s3Location)

  return new Promise((resolve, reject) => {
    try {
      let accessRoleCredentials = connectionDetail.connectionCredentials;
      let credential = new Credentials(accessRoleCredentials.accessKeyId,
        accessRoleCredentials.secretAccessKey,
        accessRoleCredentials.sessionToken)
      let region = connectionDetail.physicalEndpoints[0].awsLocation.awsRegion;
      const s3 = new AWS.S3({
        region: region,
        credentials: credential,
      });

      const params = {
        Bucket: s3Params.bucket,
        Key: s3Params.key,
        Expires: 30,
        ResponseContentType: 'text/plain;charset=UTF-8',
      };
     let url = s3.getSignedUrl('getObject', params);
     resolve(url);
    } catch(err) {
      console.log(err)
      reject(err);
    }
  });
}

