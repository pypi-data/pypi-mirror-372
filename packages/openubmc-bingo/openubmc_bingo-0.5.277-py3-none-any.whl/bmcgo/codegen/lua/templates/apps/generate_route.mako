syntax = "proto3";
import "types.proto";
import "apps/redfish/resource/schema/${filename}.proto";
import "apps/redfish/types/header.proto";
package ${filename}_${i};

message Route {
    option (url) = "/redfish/v1/${url}";
    option (auth) = true;
    message Get {
        ${filename}.${filename} Response = 1;
    }
    message Post {
        option (auth) = true;
        Header.RequestHeader header = 1;
        ${filename}.${filename} Body = 2;
        ${filename}.${filename} Response = 3;
    }
    message Patch {
        option (auth) = true;
        Header.RequestHeader header = 1;
        ${filename}.${filename} Body = 2;
        ${filename}.${filename} Response = 3;
    }
}
