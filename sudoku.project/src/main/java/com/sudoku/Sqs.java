package com.sudoku;

import software.amazon.awssdk.services.sqs.SqsClient;
import software.amazon.awssdk.services.sqs.model.*;
import java.util.List;
import java.util.ArrayList;

public class Sqs {
    private static final String QUEUE_NAME = "sudoku.fifo";

    public static SqsClient connect() {
    	return(SqsClient.builder().build());
    }

    private static SendMessageBatchResponse sendBatch(SqsClient sqs, String queueUrl, List<SendMessageBatchRequestEntry> sendmessages) {
        SendMessageBatchRequest send_batch_request = SendMessageBatchRequest.builder().queueUrl(queueUrl).entries(sendmessages).build();
        return(sqs.sendMessageBatch(send_batch_request));
    }

    public static void sendPuzzles(SqsClient sqs, List<String> puzzles) {
        GetQueueUrlRequest getQueueRequest = GetQueueUrlRequest.builder().queueName(QUEUE_NAME).build();

        String queueUrl = sqs.getQueueUrl(getQueueRequest).queueUrl();

        List<SendMessageBatchRequestEntry> sendmessages = new ArrayList<SendMessageBatchRequestEntry>();

        int counter = 0;
        for (String p : puzzles) {
            if (sendmessages.size() == 10) {
                SendMessageBatchResponse smbr = sendBatch(sqs, queueUrl, sendmessages);
                System.out.printf("response:'%s'\n", smbr.toString());
                sendmessages.clear();
                counter = 0;
            }

            long unixTime = System.currentTimeMillis();
            String id = String.format("id-%d", counter++);

            sendmessages.add(SendMessageBatchRequestEntry.builder().messageBody(p).id(id).messageGroupId("1").build());
        }

        if (sendmessages.size() > 0) {
            SendMessageBatchResponse smbr = sendBatch(sqs, queueUrl, sendmessages);
            System.out.printf("response:'%s'\n", smbr.toString());
        }
    }
}

